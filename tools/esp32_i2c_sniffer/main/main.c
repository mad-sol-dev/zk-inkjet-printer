/*
 * Passiver I2C-Mitleser fuer den Bus des Auth-Bausteins (CL-HARDWARE-REC-117).
 *
 * Kern 1 pollt SCL (GPIO32) und SDA (GPIO33) mit gesperrten Interrupts und zerlegt den Verkehr in
 * START, STOP, Bytes mit ACK/NACK. Kern 0 gibt je Transaktion eine Zeile auf UART0 (921600 Bd) aus:
 *
 *   <t in s> S E8 03 27 08 ... P       Bytes hex, angehaengtes '-' = NACK, 'Sr' = wiederholter START
 *   <t in s> WAKE 2021                 START und STOP ohne Bit dazwischen, Dauer in us (Weckpuls)
 *   !OVF <n>                           Ereignispuffer uebergelaufen, n Ereignisse verloren
 *
 * Keine I2C-Hardware des ESP32: ein Slave-Block wuerde ACKs senden und den Bus stoeren.
 * Der Master der Firmware arbeitet per Bit-Bang und schaltet SDA dicht an den SCL-Flanken
 * (CL-FIRMWARE-REC-120). Deshalb gilt ein SDA-Wechsel bei SCL high nur dann als START/STOP, wenn
 * er mehr als GUARD_US nach der steigenden und vor der fallenden SCL-Flanke liegt; sonst gehoert er
 * zur Datenleitung. Das Bit ist der SDA-Pegel waehrend der High-Phase.
 *
 * Auswertung am PC: tools/esp32_i2c_sniffer/sniff.py
 */
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/uart.h"
#include "soc/gpio_reg.h"
#include "esp_cpu.h"

#define SCL_GPIO 32
#define SDA_GPIO 33
// GPIO32..39 liegen in GPIO_IN1_REG ab Bit 0
#define SCL_BIT (1u << (SCL_GPIO - 32))
#define SDA_BIT (1u << (SDA_GPIO - 32))

#define CYCLES_PER_US CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ
#define GUARD_US 1
#define GUARD (GUARD_US * CYCLES_PER_US)

#define UART_PORT UART_NUM_0
#define LINE_IDLE_US 50000 // offene Transaktion ohne STOP nach so langer Ruhe ausgeben

enum
{
    EV_START = 1,
    EV_STOP,
    EV_BYTE,
    EV_BITS,
};

typedef struct
{
    uint64_t t; // CPU-Takte seit Start
    uint8_t kind;
    uint8_t val;
    uint8_t ack;
    uint8_t nbits;
} ev_t;

#define RING 4096
static ev_t ring[RING];
static volatile uint32_t ring_wr, ring_rd, ring_lost;

static inline void IRAM_ATTR put(uint64_t t, uint8_t kind, uint8_t val, uint8_t ack, uint8_t nbits)
{
    uint32_t w = ring_wr;
    if (w - ring_rd >= RING)
    {
        ring_lost++;
        return;
    }
    ev_t *e = &ring[w % RING];
    e->t = t;
    e->kind = kind;
    e->val = val;
    e->ack = ack;
    e->nbits = nbits;
    __sync_synchronize();
    ring_wr = w + 1;
}

static void IRAM_ATTR sniff_task(void *arg)
{
    portDISABLE_INTERRUPTS(); // dieser Kern gehoert nur noch der Abtastschleife

    uint32_t last_cc = esp_cpu_get_cycle_count();
    uint64_t hi = 0;
    uint32_t prev = REG_READ(GPIO_IN1_REG) & (SCL_BIT | SDA_BIT);

    uint64_t t_rise = 0;
    int sda_high = (prev & SDA_BIT) != 0; // SDA-Pegel der laufenden High-Phase
    int sp_in_high = 0;                   // in dieser High-Phase lag ein START/STOP
    int pend = 0;                         // SDA-Wechsel bei SCL high, noch nicht als START/STOP sicher
    uint64_t pend_t = 0;
    uint8_t pend_kind = 0;
    uint32_t bits = 0;
    int nbits = 0;

    while (1)
    {
        uint32_t cur = REG_READ(GPIO_IN1_REG) & (SCL_BIT | SDA_BIT);
        uint32_t cc = esp_cpu_get_cycle_count();
        if (cc < last_cc)
        {
            hi += 1ULL << 32;
        }
        last_cc = cc;
        uint64_t t = hi | cc;

        // ein SDA-Wechsel, dem GUARD lang keine fallende SCL-Flanke folgt, ist START oder STOP
        if (pend && t - pend_t > GUARD)
        {
            if (nbits)
            {
                put(pend_t, EV_BITS, bits, 0, nbits);
            }
            put(pend_t, pend_kind, 0, 0, 0);
            bits = 0;
            nbits = 0;
            pend = 0;
            sp_in_high = 1;
        }
        if (cur == prev)
        {
            continue;
        }
        int scl = (cur & SCL_BIT) != 0;
        int sda = (cur & SDA_BIT) != 0;
        int pscl = (prev & SCL_BIT) != 0;
        int psda = (prev & SDA_BIT) != 0;
        prev = cur;

        if (scl && !pscl)
        {
            t_rise = t;
            sda_high = sda;
            sp_in_high = 0;
        }
        else if (!scl && pscl)
        {
            int bit_valid = !sp_in_high;
            if (pend) // SDA wechselte knapp vor der fallenden Flanke: gehoert zur Low-Phase
            {
                pend = 0;
                bit_valid = 1;
            }
            if (bit_valid)
            {
                bits = (bits << 1) | (uint32_t)sda_high;
                if (++nbits == 9)
                {
                    put(t_rise, EV_BYTE, bits >> 1, !(bits & 1), 8);
                    bits = 0;
                    nbits = 0;
                }
            }
        }
        else if (scl && sda != psda)
        {
            if (t - t_rise <= GUARD) // Daten kamen knapp nach der steigenden Flanke
            {
                sda_high = sda;
            }
            else
            {
                if (pend) // zweiter Wechsel in derselben High-Phase: der erste war echt
                {
                    if (nbits)
                    {
                        put(pend_t, EV_BITS, bits, 0, nbits);
                    }
                    put(pend_t, pend_kind, 0, 0, 0);
                    bits = 0;
                    nbits = 0;
                    sp_in_high = 1;
                }
                pend = 1;
                pend_t = t;
                pend_kind = sda ? EV_STOP : EV_START;
            }
        }
        // SDA-Wechsel bei SCL low: Datenvorbereitung, nichts zu tun
    }
}

static void out(const char *s, int n)
{
    uart_write_bytes(UART_PORT, s, n);
}

static int fmt_t(char *p, uint64_t t)
{
    uint64_t us = t / CYCLES_PER_US;
    return sprintf(p, "%llu.%06llu", us / 1000000, us % 1000000);
}

void app_main(void)
{
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << SCL_GPIO) | (1ULL << SDA_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io);

    uart_driver_install(UART_PORT, 256, 16384, 0, NULL, 0);
    uart_set_baudrate(UART_PORT, 921600);

    xTaskCreatePinnedToCore(sniff_task, "sniff", 4096, NULL, configMAX_PRIORITIES - 1, NULL, 1);

    static char line[4096];
    int len = 0;
    int open = 0;      // Transaktion begonnen, STOP noch nicht gesehen
    int content = 0;   // Bytes oder Bits seit dem START
    uint64_t t_start = 0, t_last = 0;
    uint32_t lost_seen = 0;
    uint32_t idle_ticks = 0;

    len = sprintf(line, "\n# esp32_i2c_sniffer SCL=GPIO%d SDA=GPIO%d guard=%dus\n", SCL_GPIO, SDA_GPIO, GUARD_US);
    out(line, len);
    len = 0;

    while (1)
    {
        if (ring_rd == ring_wr)
        {
            if (ring_lost != lost_seen)
            {
                char m[32];
                int n = sprintf(m, "!OVF %lu\n", (unsigned long)(ring_lost - lost_seen));
                lost_seen = ring_lost;
                out(m, n);
            }
            // offene Transaktion ohne STOP nach einer Weile Ruhe trotzdem ausgeben
            if (open && content && ++idle_ticks * portTICK_PERIOD_MS * 1000 > LINE_IDLE_US)
            {
                len += sprintf(line + len, " ...\n");
                out(line, len);
                len = 0;
                open = 0;
                content = 0;
            }
            vTaskDelay(1);
            continue;
        }
        ev_t e = ring[ring_rd % RING];
        __sync_synchronize();
        ring_rd++;
        idle_ticks = 0;
        t_last = e.t;

        switch (e.kind)
        {
        case EV_START:
            if (open && content)
            {
                len += sprintf(line + len, " Sr");
            }
            else
            {
                len = fmt_t(line, e.t);
                len += sprintf(line + len, " S");
                t_start = e.t;
                content = 0;
            }
            open = 1;
            break;
        case EV_BYTE:
            if (!open)
            {
                len = fmt_t(line, e.t);
                len += sprintf(line + len, " ?");
                open = 1;
            }
            len += sprintf(line + len, e.ack ? " %02X" : " %02X-", e.val);
            content = 1;
            break;
        case EV_BITS:
            if (open)
            {
                len += sprintf(line + len, " b%d:%lx", e.nbits, (unsigned long)e.val);
                content = 1;
            }
            break;
        case EV_STOP:
            if (open && !content)
            {
                len = fmt_t(line, t_start);
                len += sprintf(line + len, " WAKE %llu\n", (t_last - t_start) / CYCLES_PER_US);
            }
            else if (open)
            {
                len += sprintf(line + len, " P\n");
            }
            else
            {
                len = fmt_t(line, e.t);
                len += sprintf(line + len, " P\n");
            }
            out(line, len);
            len = 0;
            open = 0;
            content = 0;
            break;
        }
        if (len > (int)sizeof(line) - 64) // ueberlange Transaktion stueckeln
        {
            line[len++] = '\n';
            out(line, len);
            len = sprintf(line, "  +");
        }
    }
}

typedef unsigned char   undefined;

typedef unsigned char    byte;
typedef struct __fpos64_t __fpos64_t, *P__fpos64_t;

struct __fpos64_t {
    byte __pos;
    byte __state;
};

typedef struct __fpos_t __fpos_t, *P__fpos_t;

struct __fpos_t {
    byte __pos;
    byte __state;
};

typedef struct __fsid_t __fsid_t, *P__fsid_t;

struct __fsid_t {
    byte __val[2];
};

typedef struct __once_flag __once_flag, *P__once_flag;

struct __once_flag {
    byte __data;
};

typedef struct __pthread_list_t __pthread_list_t, *P__pthread_list_t;

struct __pthread_list_t {
    byte *__prev;
    byte *__next;
};

typedef struct __pthread_slist_t __pthread_slist_t, *P__pthread_slist_t;

struct __pthread_slist_t {
    byte *__next;
};

typedef struct __sigset_t __sigset_t, *P__sigset_t;

struct __sigset_t {
    byte int)))];
};

typedef struct __value __value, *P__value;

struct __value {
    byte __count;
    byte __wch;
    byte __wchb[4];
};

typedef enum AU_CODEC_E {
    MFL_CODEC_UNKNOWN=1000
} AU_CODEC_E;

typedef enum AU_PLAY_DEV_E {
    MFL_PLAY_AC97=0,
    MFL_PLAY_I2S=1,
    MFL_PLAY_UDA1345TS=2,
    MFL_PLAY_DAC=4,
    MFL_PLAY_MA3=5,
    MFL_PLAY_MA5=6,
    MFL_PLAY_W5691=7,
    MFL_PLAY_WM8753=8,
    MFL_PLAY_WM8751=9,
    MFL_PLAY_WM8978=10,
    MFL_PLAY_MA5I=11,
    MFL_PLAY_MA5SI=12,
    MFL_PLAY_W56964=13,
    MFL_PLAY_AK4569=14,
    MFL_PLAY_TIAIC31=15,
    MFL_PLAY_WM8731=16
} AU_PLAY_DEV_E;

typedef enum AU_REC_DEV_E {
    MFL_REC_AC97=0,
    MFL_REC_I2S=1,
    MFL_REC_UDA1345TS=2,
    MFL_REC_ADC=3,
    MFL_REC_W5691=7,
    MFL_REC_WM8753=8,
    MFL_REC_WM8751=9,
    MFL_REC_WM8978=10,
    MFL_REC_AK4569=14,
    MFL_REC_TIAIC31=15,
    MFL_REC_WM8731=16
} AU_REC_DEV_E;

typedef enum AU_SRATE_E {
    AU_SRATE_8000=8000,
    AU_SRATE_11025=11025,
    AU_SRATE_12000=12000,
    AU_SRATE_16000=16000,
    AU_SRATE_22050=22050,
    AU_SRATE_24000=24000,
    AU_SRATE_32000=32000,
    AU_SRATE_44100=44100,
    AU_SRATE_48000=48000
} AU_SRATE_E;

typedef enum AU_TYPE_E {
} AU_TYPE_E;

typedef struct AVI_INFO_T AVI_INFO_T, *PAVI_INFO_T;

struct AVI_INFO_T {
    byte uMovieLength;
    byte uPlayCurTimePos;
    byte eAuCodec;
    byte nAuPlayChnNum;
    byte nAuPlaySRate;
    byte uVideoFrameRate;
    byte usImageWidth;
    byte usImageHeight;
    byte uVidTotalFrames;
    byte uVidFramesPlayed;
    byte uVidFramesSkipped;
};

typedef struct CaptureFilter CaptureFilter, *PCaptureFilter;

struct CaptureFilter {
    byte Brightness;
    byte Contrast;
    byte Hue;
    byte POWER_LINE_FREQUENCY;
    byte Saturation;
    byte Sharpness;
    byte Gamma;
    byte Backlight;
};

typedef struct COLORMATCHDESCRIPTOR COLORMATCHDESCRIPTOR, *PCOLORMATCHDESCRIPTOR;

struct COLORMATCHDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bColorPrimaries;
    byte bTransferCharacteristics;
    byte bMatrixCoefficients;
};

typedef struct CONFIGDESCRIPTOR CONFIGDESCRIPTOR, *PCONFIGDESCRIPTOR;

struct CONFIGDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte wTotalLength;
    byte bNumInterfaces;
    byte bConfigurationValue;
    byte iConfiguration;
    byte bmAttributes;
    byte bMaxPower;
};

typedef struct CSFORMATDESCRIPTOR_MJPEG CSFORMATDESCRIPTOR_MJPEG, *PCSFORMATDESCRIPTOR_MJPEG;

struct CSFORMATDESCRIPTOR_MJPEG {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bFormatIndex;
    byte bNumFrameDescriptors;
    byte bmFlags;
    byte bDefaultFrameIndex;
    byte bAspectRatioX;
    byte bAspectRatioY;
    byte bmInterlaceFlags;
    byte bCopyProtect;
};

typedef struct CSFRAMEDESCRIPTOR_MJPEG CSFRAMEDESCRIPTOR_MJPEG, *PCSFRAMEDESCRIPTOR_MJPEG;

struct CSFRAMEDESCRIPTOR_MJPEG {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bFrameIndex;
    byte bmCapabilities;
    byte wWidth;
    byte wHeight;
    byte dwMinBitRate;
    byte dwMaxBitRate;
    byte dwMaxVideoFrameBufSize;
    byte dwDefaultFrameInterval;
    byte bFrameIntervalType;
    byte dwMinFrameInterval_1;
    byte dwMinFrameInterval_2;
    byte dwMinFrameInterval_3;
    byte dwMinFrameInterval_4;
    byte dwMinFrameInterval_5;
    byte dwMinFrameInterval_6;
};

typedef struct CSHEADERDESCRIPTOR CSHEADERDESCRIPTOR, *PCSHEADERDESCRIPTOR;

struct CSHEADERDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bNumFormats;
    byte wTotalLength;
    byte bEndpointAddress;
    byte bmInfo;
    byte bTerminalLink;
    byte bStillCaptureMethod;
    byte bTriggerSupport;
    byte bTriggerUsage;
    byte bControlSize;
    byte bmaControls0;
};

typedef struct CSHEADERDESCRIPTOR_BOTH CSHEADERDESCRIPTOR_BOTH, *PCSHEADERDESCRIPTOR_BOTH;

struct CSHEADERDESCRIPTOR_BOTH {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bNumFormats;
    byte wTotalLength;
    byte bEndpointAddress;
    byte bmInfo;
    byte bTerminalLink;
    byte bStillCaptureMethod;
    byte bTriggerSupport;
    byte bTriggerUsage;
    byte bControlSize;
    byte bmaControls0;
    byte bmaControls1;
};

typedef struct CSINTERFACEDESCRIPTOR CSINTERFACEDESCRIPTOR, *PCSINTERFACEDESCRIPTOR;

struct CSINTERFACEDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bcdUVC;
    byte wTotalLength;
    byte dwClockFrequency;
    byte bInCollection;
    byte baInterfaceNr;
};

typedef struct CSINTERRUPTEPDESCRIPTOR CSINTERRUPTEPDESCRIPTOR, *PCSINTERRUPTEPDESCRIPTOR;

struct CSINTERRUPTEPDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte wMaxPacketSize;
};

typedef struct CSSTILLFRAMEDESCRIPTOR CSSTILLFRAMEDESCRIPTOR, *PCSSTILLFRAMEDESCRIPTOR;

struct CSSTILLFRAMEDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bEndpointAddress;
    byte bNumImageSizePatterns;
    byte wWidth_1;
    byte wHeight_1;
    byte wWidth_2;
    byte wHeight_2;
    byte wWidth_3;
    byte wHeight_3;
    byte bNumCompressionPtn;
};

typedef struct DateTime_T DateTime_T, *PDateTime_T;

struct DateTime_T {
    byte year;
    byte mon;
    byte day;
    byte hour;
    byte min;
    byte sec;
};

typedef struct DEV_REQ_T DEV_REQ_T, *PDEV_REQ_T;

struct DEV_REQ_T {
    byte requesttype;
    byte request;
    byte value;
    byte index;
    byte length;
};

typedef struct DEVICEDESCRIPTOR DEVICEDESCRIPTOR, *PDEVICEDESCRIPTOR;

struct DEVICEDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bcdUSB;
    byte bDeviceClass;
    byte bDeviceSubClass;
    byte bDeviceProtocol;
    byte bMaxPacketSize0;
    byte idVendor;
    byte idProduct;
    byte bcdDevice;
    byte iManufacturer;
    byte iProduct;
    byte iSerialNumber;
    byte bNumConfigurations;
};

typedef struct DIR_ENT_T DIR_ENT_T, *PDIR_ENT_T;

struct DIR_ENT_T {
    byte pucDirName[8];
    byte pucDirExtName[3];
    byte ucDirAttrib;
    byte ucDirNTRes;
    byte ucDirCTimeTenth;
    byte pucDirCTime[2];
    byte pucDirCDate[2];
    byte pucDirLADate[2];
    byte pucDirFirstClusHi[2];
    byte pucDirWTime[2];
    byte pucDirWDate[2];
    byte pucDirFirstClusLo[2];
    byte pucDirFileSize[4];
};

typedef struct DISK_OP_T DISK_OP_T, *PDISK_OP_T;

struct DISK_OP_T {
    byte *);
    byte *);
    byte *);
    byte BOOL);
    byte BOOL);
    byte *);
};

typedef struct Disk_Par_Info Disk_Par_Info, *PDisk_Par_Info;

struct Disk_Par_Info {
    byte free_size;
    byte NumCyl;
    byte fat16flg;
};

typedef struct div_t div_t, *Pdiv_t;

struct div_t {
    byte quot;
    byte rem;
};

typedef enum DRVI2S_SYS_CLOCK_E {
    eDRVI2S_256FS=0
} DRVI2S_SYS_CLOCK_E;

typedef enum E_DRVEDMA_APB_DEVICE {
    eDRVEDMA_SPIMS0=0
} E_DRVEDMA_APB_DEVICE;

typedef enum E_DRVEDMA_APB_RW {
    eDRVEDMA_READ_APB=0
} E_DRVEDMA_APB_RW;

typedef enum E_DRVEDMA_CHANNEL_INDEX {
    eDRVEDMA_CHANNEL_0=0
} E_DRVEDMA_CHANNEL_INDEX;

typedef enum E_DRVEDMA_COLOR_FORMAT {
    eDRVEDMA_RGB888=1,
    eDRVEDMA_RGB555=2,
    eDRVEDMA_RGB565=4,
    eDRVEDMA_YCbCr422=8
} E_DRVEDMA_COLOR_FORMAT;

typedef enum E_DRVEDMA_DIRECTION_SELECT {
    eDRVEDMA_DIRECTION_INCREMENTED=0
} E_DRVEDMA_DIRECTION_SELECT;

typedef enum E_DRVEDMA_INT_ENABLE {
    eDRVEDMA_TABORT=1,
    eDRVEDMA_WAR=4,
    eDRVEDMA_SG=8
} E_DRVEDMA_INT_ENABLE;

typedef enum E_DRVEDMA_INT_FLAG {
    eDRVEDMA_TABORT_FLAG=1,
    eDRVEDMA_SG_FLAG=8,
    eDRVEDMA_WRA_EMPTY_FLAG=256,
    eDRVEDMA_WRA_THREE_FOURTHS_FLAG=512,
    eDRVEDMA_WRA_HALF_FLAG=1024,
    eDRVEDMA_WRA_QUARTER_FLAG=2048
} E_DRVEDMA_INT_FLAG;

typedef enum E_DRVEDMA_MODE_SELECT {
    eDRVEDMA_MEMORY_TO_MEMORY=0
} E_DRVEDMA_MODE_SELECT;

typedef enum E_DRVEDMA_OPERATION {
    eDRVEDMA_DISABLE=0
} E_DRVEDMA_OPERATION;

typedef enum E_DRVEDMA_TARGET {
    eDRVEDMA_TARGET_SOURCE=0
} E_DRVEDMA_TARGET;

typedef enum E_DRVEDMA_TRANSFER_WIDTH {
    eDRVEDMA_WIDTH_32BITS=0
} E_DRVEDMA_TRANSFER_WIDTH;

typedef enum E_DRVEDMA_WRAPAROUND_SELECT {
    eDRVEDMA_WRAPAROUND_NO_INT=0,
    eDRVEDMA_WRAPAROUND_HALF=4,
    eDRVEDMA_WRAPAROUND_QUARTER=8
} E_DRVEDMA_WRAPAROUND_SELECT;

typedef enum E_DRVI2S_CHANNEL {
} E_DRVI2S_CHANNEL;

typedef enum E_DRVI2S_FORMAT {
    eDRVI2S_I2S=0
} E_DRVI2S_FORMAT;

typedef enum E_DRVI2S_SAMPLING {
    eDRVI2S_FREQ_8000=8000,
    eDRVI2S_FREQ_11025=11025,
    eDRVI2S_FREQ_12000=12000,
    eDRVI2S_FREQ_16000=16000,
    eDRVI2S_FREQ_22050=22050,
    eDRVI2S_FREQ_24000=24000,
    eDRVI2S_FREQ_32000=32000,
    eDRVI2S_FREQ_44100=44100,
    eDRVI2S_FREQ_48000=48000,
    eDRVI2S_FREQ_64000=64000,
    eDRVI2S_FREQ_88200=88200,
    eDRVI2S_FREQ_96000=96000
} E_DRVI2S_SAMPLING;

typedef enum E_DRVSPI_OPERATION {
    eDRVSPI_DISABLE=0
} E_DRVSPI_OPERATION;

typedef enum E_DRVSPU_CHANNEL {
    eDRVSPU_CHANNEL_0=0
} E_DRVSPU_CHANNEL;

typedef enum E_DRVSPU_EQ_BAND {
    eDRVSPU_EQBAND_DC=0
} E_DRVSPU_EQ_BAND;

typedef enum E_DRVSPU_EQ_GAIN {
    eDRVSPU_EQGAIN_M7DB=0
} E_DRVSPU_EQ_GAIN;

typedef enum E_DRVSPU_SAMPLING {
    eDRVSPU_FREQ_8000=8000,
    eDRVSPU_FREQ_11025=11025,
    eDRVSPU_FREQ_12000=12000,
    eDRVSPU_FREQ_16000=16000,
    eDRVSPU_FREQ_22050=22050,
    eDRVSPU_FREQ_24000=24000,
    eDRVSPU_FREQ_32000=32000,
    eDRVSPU_FREQ_44100=44100,
    eDRVSPU_FREQ_48000=48000
} E_DRVSPU_SAMPLING;

typedef enum E_DRVVPOST_8BIT_SYNCLCM_INTERFACE {
    eDRVVPOST_SRGB_YUV422=0
} E_DRVVPOST_8BIT_SYNCLCM_INTERFACE;

typedef enum E_DRVVPOST_CCIR656_MODE {
    eDRVVPOST_CCIR656_360=0
} E_DRVVPOST_CCIR656_MODE;

typedef enum E_DRVVPOST_DATABUS {
    eDRVVPOST_DATA_8BITS=0
} E_DRVVPOST_DATABUS;

typedef enum E_DRVVPOST_ENDIAN {
    eDRVVPOST_YUV_BIG_ENDIAN=0
} E_DRVVPOST_ENDIAN;

typedef enum E_DRVVPOST_FRAME_DATA_TYPE {
    eDRVVPOST_FRAME_RGB555=0
} E_DRVVPOST_FRAME_DATA_TYPE;

typedef enum E_DRVVPOST_IMAGE_SCALING {
    eDRVVPOST_DUPLICATED=0
} E_DRVVPOST_IMAGE_SCALING;

typedef enum E_DRVVPOST_IMAGE_SOURCE {
    eDRVVPOST_RESERVED=0
} E_DRVVPOST_IMAGE_SOURCE;

typedef enum E_DRVVPOST_INT {
    eDRVVPOST_HINT=1,
    eDRVVPOST_VINT=2,
    eDRVVPOST_TVFIELDINT=4,
    eDRVVPOST_MPUCPLINT=16
} E_DRVVPOST_INT;

typedef enum E_DRVVPOST_LCM_TYPE {
    eDRVVPOST_HIGH_RESOLUTINO_SYNC=0,
    eDRVVPOST_SYNC=1,
    eDRVVPOST_MPU=3
} E_DRVVPOST_LCM_TYPE;

typedef enum E_DRVVPOST_MPU_TYPE {
    eDRVVPOST_I80=0
} E_DRVVPOST_MPU_TYPE;

typedef enum E_DRVVPOST_MPULCM_DATABUS {
    eDRVVPOST_MPU_8_8=0
} E_DRVVPOST_MPULCM_DATABUS;

typedef enum E_DRVVPOST_OSD_CTL {
    eOSD_SHOW=1
} E_DRVVPOST_OSD_CTL;

typedef enum E_DRVVPOST_PARALLEL_SYNCLCM_INTERFACE {
    eDRVVPOST_PRGB_16BITS=0
} E_DRVVPOST_PARALLEL_SYNCLCM_INTERFACE;

typedef enum E_DRVVPOST_SERAIL_SYNCLCM_COLOR_ORDER {
    eDRVVPOST_SRGB_RGB=0
} E_DRVVPOST_SERAIL_SYNCLCM_COLOR_ORDER;

typedef enum E_DRVVPOST_SYNCLCM_DATABUS {
    eDRVVPOST_SYNC_8BITS=0
} E_DRVVPOST_SYNCLCM_DATABUS;

typedef enum E_DRVVPOST_TIMING_TYPE {
    eDRVVPOST_SYNC_TV=0
} E_DRVVPOST_TIMING_TYPE;

typedef enum E_RTC_CMD {
    RTC_IOC_IDENTIFY_LEAP_YEAR=0,
    RTC_IOC_SET_TICK_MODE=1,
    RTC_IOC_GET_TICK=2,
    RTC_IOC_RESTORE_TICK=3,
    RTC_IOC_ENABLE_INT=4,
    RTC_IOC_DISABLE_INT=5,
    RTC_IOC_SET_CURRENT_TIME=6,
    RTC_IOC_SET_ALAMRM_TIME=7,
    RTC_IOC_SET_FREQUENCY=8,
    RTC_IOC_SET_POWER_ON=9,
    RTC_IOC_SET_POWER_OFF=10,
    RTC_IOC_SET_POWER_OFF_PERIOD=11,
    RTC_IOC_ENABLE_HW_POWEROFF=12,
    RTC_IOC_DISABLE_HW_POWEROFF=13,
    RTC_IOC_GET_POWERKEY_STATUS=14,
    RTC_IOC_SET_PSWI_CALLBACK=15
} E_RTC_CMD;

typedef enum E_RTC_DWR_PARAMETER {
    RTC_SUNDAY=0,
    RTC_MONDAY=1,
    RTC_TUESDAY=2,
    RTC_WEDNESDAY=3,
    RTC_THURSDAY=4,
    RTC_FRIDAY=5,
    RTC_SATURDAY=6
} E_RTC_DWR_PARAMETER;

typedef enum E_RTC_TIME_SELECT {
    RTC_CURRENT_TIME=0,
    RTC_ALARM_TIME=1
} E_RTC_TIME_SELECT;

typedef enum E_SYS_SRC_CLK {
    eSYS_EXT=0,
    eSYS_X32K=1,
    eSYS_APLL=2,
    eSYS_UPLL=3
} E_SYS_SRC_CLK;

typedef enum E_VIDEOIN_BUFFER {
    eVIDEOIN_BUF0=0
} E_VIDEOIN_BUFFER;

typedef enum E_VIDEOIN_DEV_TYPE {
    eVIDEOIN_SNR_CCIR601=0
} E_VIDEOIN_DEV_TYPE;

typedef enum E_VIDEOIN_IN_FORMAT {
    eVIDEOIN_IN_YUV422=0
} E_VIDEOIN_IN_FORMAT;

typedef enum E_VIDEOIN_INT_TYPE {
    eVIDEOIN_VINT=65536,
    eVIDEOIN_MEINT=131072,
    eVIDEOIN_ADDRMINT=524288,
    eVIDEOIN_MDINT=1048576
} E_VIDEOIN_INT_TYPE;

typedef enum E_VIDEOIN_ORDER {
    eVIDEOIN_IN_UYVY=0
} E_VIDEOIN_ORDER;

typedef enum E_VIDEOIN_OUT_FORMAT {
    eVIDEOIN_OUT_YUV422=0
} E_VIDEOIN_OUT_FORMAT;

typedef enum E_VIDEOIN_PIPE {
    eVIDEOIN_BOTH_PIPE_DISABLE=0,
    eVIDEOIN_PLANAR=1,
    eVIDEOIN_PACKET=2,
    eVIDEOIN_BOTH_PIPE_ENABLE=3
} E_VIDEOIN_PIPE;

typedef enum E_VIDEOIN_SNR_SRC {
    eVIDEOIN_SNR_APLL=2,
    eVIDEOIN_SNR_UPLL=3
} E_VIDEOIN_SNR_SRC;

typedef enum E_VIDEOIN_TYPE {
    eVIDEOIN_TYPE_CCIR601=0
} E_VIDEOIN_TYPE;

typedef struct ENDPOINTDESCRIPTOR ENDPOINTDESCRIPTOR, *PENDPOINTDESCRIPTOR;

struct ENDPOINTDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bEndpointAddress;
    byte bmAttributes;
    byte wMaxPacketSize;
    byte bInterval;
};

typedef enum EQ_EFT_E {
    EQ_DEFAULT=0
} EQ_EFT_E;

typedef struct FAT_FCB_T FAT_FCB_T, *PFAT_FCB_T;

struct FAT_FCB_T {
    byte szShortName[14];
    byte ucDirAttrib;
    byte ucDirNTRes;
    byte ucDirCTimeTenth;
    byte dirCtime;
    byte usDirCDate;
    byte usDirLDate;
    byte usDirWTime;
    byte usDirWDate;
    byte uDirEntSecNo;
    byte nDirEntInSecOffset;
    byte bIsFat16Root;
    byte bIsRWBuffDirty;
    byte *pucRWBuff;
    byte n64RWBuffMapPos;
    byte uRWBuffSecNo;
    byte nRWBuffSecCnt;
    byte nClusCnt;
    byte uRWBuffSize;
    byte *pucCCBuff;
    byte uCCBuffSize;
    byte uCCEntCnt;
    byte uCCDoneFPos;
    byte uFirstClusNo;
    byte uLastClusNo;
    byte uCurClusNo;
    byte n64FileSize;
    byte n64FilePos;
};

typedef struct FAT_INFO_T FAT_INFO_T, *PFAT_INFO_T;

struct FAT_INFO_T {
    byte uBpbBytesPerSec;
    byte uBpbSecPerClus;
    byte usBpbRsvdSecCnt;
    byte ucBpbNumFATs;
    byte usBpbRootEntCnt;
    byte uBpbTotalSectors;
    byte ucBpbMedia;
    byte uBpbFatSize;
    byte usBpbSecPerTrk;
    byte usBpbNumHeads;
    byte uBpbHiddSec;
    byte uBsVolID;
    byte sBsVolLab[12];
    byte uBpbRootClus;
    byte usBpbFsInfo;
    byte uEndClusMark;
    byte ucFatType;
    byte uSecSzMask;
    byte uBytesPerClus;
    byte uLastSecNo;
    byte uLastClusNo;
    byte uFatSecStart;
    byte uDataSecStart;
    byte uRootDirStartSec;
    byte uFsInfoSecNo;
    byte uFreeClusSearchIdx;
    byte uTotalFreeClus;
    byte pucFSInfo[512];
};

typedef struct fd_set fd_set, *Pfd_set;

struct fd_set {
    byte (__fd_mask))];
};

typedef struct FDRV_T FDRV_T, *PFDRV_T;

struct FDRV_T {
    byte nDiskType;
    byte nDiskInstance;
    byte nDriveNo;
    byte nPartitionNo;
    byte *ptPDisk;
};

typedef struct FeatureFilter FeatureFilter, *PFeatureFilter;

struct FeatureFilter {
    byte Mute;
    byte Volume;
};

typedef struct FILE_FIND_T FILE_FIND_T, *PFILE_FIND_T;

struct FILE_FIND_T {
    byte hFile;
    byte +2];
    byte szShortName[14];
    byte ucAttrib;
    byte ucCTimeMS;
    byte ucCTimeSec;
    byte ucCTimeMin;
    byte ucCTimeHour;
    byte ucCDateDay;
    byte ucCDateMonth;
    byte ucCDateYear;
    byte ucLDateDay;
    byte ucLDateMonth;
    byte ucLDateYear;
    byte ucWTimeSec;
    byte ucWTimeMin;
    byte ucWTimeHour;
    byte ucWDateDay;
    byte ucWDateMonth;
    byte ucWDateYear;
    byte n64FileSize;
    byte *suPattern[8];
    byte bIsPatternExcludeDir;
    byte eFileSorting;
    byte bIsDirFirst;
    byte bIsAllDirSearched;
    byte bHasSearchPattern;
    byte nCandidatePos;
    byte nLastChoicePos;
    byte *ptCandidate;
    byte *ptLastChoice;
};

typedef struct FILE_OP_T FILE_OP_T, *PFILE_OP_T;

struct FILE_OP_T {
    byte *);
    byte *);
    byte INT*);
    byte *);
    byte INT64);
    byte INT64);
    byte *);
    byte *);
    byte *);
    byte *);
    byte *);
    byte *);
};

typedef enum FILE_SORTING_T {
    NO_SORTING=0
} FILE_SORTING_T;

typedef struct FILE_STAT_T FILE_STAT_T, *PFILE_STAT_T;

struct FILE_STAT_T {
    byte uFlag;
    byte ucAttrib;
    byte ucDirNTRes;
    byte ucCTimeMs;
    byte ucCTimeSec;
    byte ucCTimeMin;
    byte ucCTimeHour;
    byte ucCDateDay;
    byte ucCDateMonth;
    byte ucCDateYear;
    byte ucLDateDay;
    byte ucLDateMonth;
    byte ucLDateYear;
    byte ucWTimeSec;
    byte ucWTimeMin;
    byte ucWTimeHour;
    byte ucWDateDay;
    byte ucWDateMonth;
    byte ucWDateYear;
    byte uDev;
    byte uUnique;
    byte n64FilePos;
    byte n64FileSize;
};

typedef struct FILE_T FILE_T, *PFILE_T;

struct FILE_T {
    byte szFnameAscii[257];
    byte uFlag;
    byte *ptLDisk;
    byte tFatFcb;
    byte *ptFileOP;
    byte *ptFileAllLink;
    byte *ptFileDiskLink;
};

typedef struct FMI_SD_INFO_T FMI_SD_INFO_T, *PFMI_SD_INFO_T;

struct FMI_SD_INFO_T {
    byte uCardType;
    byte uRCA;
    byte bIsCardInsert;
};

typedef struct FMI_SM_INFO_T FMI_SM_INFO_T, *PFMI_SM_INFO_T;

struct FMI_SM_INFO_T {
    byte uSectorPerFlash;
    byte uBlockPerFlash;
    byte uPagePerBlock;
    byte uSectorPerBlock;
    byte uLibStartBlock;
    byte nPageSize;
    byte uBadBlockCount;
    byte bIsMulticycle;
    byte bIsMLCNand;
    byte bIsNandECC4;
    byte bIsNandECC8;
    byte bIsNandECC12;
    byte bIsNandECC15;
    byte bIsCheckECC;
};

typedef struct FRAMEDESCRIPTOR_1 FRAMEDESCRIPTOR_1, *PFRAMEDESCRIPTOR_1;

struct FRAMEDESCRIPTOR_1 {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bFrameIndex;
    byte bmCapabilities;
    byte wWidth;
    byte wHeight;
    byte dwMinBitRate;
    byte dwMaxBitRate;
    byte dwMaxVideoFrameBufferSize;
    byte dwDefaultFrameInterval;
    byte bFrameIntervalType;
    byte dwMinFrameInterval_1;
    byte dwMinFrameInterval_2;
    byte dwMinFrameInterval_3;
    byte dwMinFrameInterval_4;
    byte dwMinFrameInterval_5;
    byte dwMinFrameInterval_6;
};

typedef struct FRAMEDESCRIPTOR_2 FRAMEDESCRIPTOR_2, *PFRAMEDESCRIPTOR_2;

struct FRAMEDESCRIPTOR_2 {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bFrameIndex;
    byte bmCapabilities;
    byte wWidth;
    byte wHeight;
    byte dwMinBitRate;
    byte dwMaxBitRate;
    byte dwMaxVideoFrameBufferSize;
    byte dwDefaultFrameInterval;
    byte bFrameIntervalType;
    byte dwMinFrameInterval_1;
    byte dwMinFrameInterval_2;
    byte dwMinFrameInterval_3;
};

typedef struct IADDESCRIPTOR IADDESCRIPTOR, *PIADDESCRIPTOR;

struct IADDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bFirstInterface;
    byte bInterfaceCount;
    byte bFunctionClass;
    byte bFunctionSubClass;
    byte bFunctionProtocol;
    byte iFunction;
};

typedef struct ID3_ENT_T ID3_ENT_T, *PID3_ENT_T;

struct ID3_ENT_T {
    byte nLength;
    byte sTag[128];
    byte bIsUnicode;
};

typedef struct ID3_PIC_T ID3_PIC_T, *PID3_PIC_T;

struct ID3_PIC_T {
    byte bHasPic;
    byte cType;
    byte tTitle;
    byte nPicOffset;
    byte nPicSize;
    byte *ptNextPic;
};

typedef struct ID3_TAG_T ID3_TAG_T, *PID3_TAG_T;

struct ID3_TAG_T {
    byte tTitle;
    byte tArtist;
    byte tAlbum;
    byte tComment;
    byte szYear[16];
    byte szTrack[16];
    byte szGenre[16];
    byte cVersion;
    byte tPicture;
};

typedef struct INPUTTERMINALDESCRIPTOR INPUTTERMINALDESCRIPTOR, *PINPUTTERMINALDESCRIPTOR;

struct INPUTTERMINALDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bTerminalID;
    byte wTerminalType;
    byte bAssocTerminal;
    byte iTerminal;
    byte wObjectiveFocalLengthMin;
    byte wObjectiveFocalLengthMax;
    byte wOcularFocalLength;
    byte bControlSize;
    byte bmControls;
};

typedef enum INT_SOURCE_E {
    IRQ_WDT=1,
    IRQ_EXTINT0=2,
    IRQ_EXTINT1=3,
    IRQ_EXTINT2=4,
    IRQ_EXTINT3=5,
    IRQ_SPU=6,
    IRQ_I2S=7,
    IRQ_VPOST=8,
    IRQ_VIDEOIN=9,
    IRQ_GPU=10,
    IRQ_BLT=11,
    IRQ_FSC=12,
    IRQ_HUART=13,
    IRQ_TMR0=14,
    IRQ_TMR1=15,
    IRQ_UDC=16,
    IRQ_SIC=17,
    IRQ_UHC=18,
    IRQ_EDMA=19,
    IRQ_SPIMS0=20,
    IRQ_SPIMS1=21,
    IRQ_ADC=22,
    IRQ_RTC=23,
    IRQ_UART=24,
    IRQ_PWM=25,
    IRQ_JPG=26,
    IRQ_KPI=28,
    IRQ_DES=29,
    IRQ_I2C=30,
    IRQ_PWR=31
} INT_SOURCE_E;

typedef struct INTERFACEDESCRIPTOR INTERFACEDESCRIPTOR, *PINTERFACEDESCRIPTOR;

struct INTERFACEDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bInterfceNumber;
    byte bAlternateSetting;
    byte bNumEndpoints;
    byte bInterfaceClass;
    byte bInterfaceSubClass;
    byte bInterfaceProtocol;
    byte iInterface;
};

typedef enum JV_MODE_E {
} JV_MODE_E;

typedef struct KTV_CFG_T KTV_CFG_T, *PKTV_CFG_T;

struct KTV_CFG_T {
    byte eAuCodecType;
    byte *suInMP4File;
    byte *suInAudioFile;
    byte *suInLyricFile;
    byte *suOutMediaFile;
    byte *szOMFAscii;
    byte *suOutMetaFile;
    byte *szOTFAscii;
    byte bStopIfVideoEnd;
    byte bStopIfAudioEnd;
    byte nVideoClipStart;
    byte nVideoClipEnd;
    byte nAudioClipStart;
    byte nAudioClipEnd;
    byte bUseTempFile;
    byte nMP4VidMaxSSize;
    byte *ptMvCfgKtv);
    byte *ptMvCfgKtv);
    byte tMvCfgMp4;
    byte tMvCfgAu;
    byte tMvCfgKtv;
};

typedef struct L2PM_T L2PM_T, *PL2PM_T;

struct L2PM_T {
    byte pba;
    byte reserved;
};

typedef struct LDISK_T LDISK_T, *PLDISK_T;

struct LDISK_T {
    byte *ptPDisk;
    byte nDriveNo;
    byte ucFileSysType;
    byte bIsDiskRemoved;
    byte szVolLabel[16];
    byte uDiskSize;
    byte uFreeSpace;
    byte tFatInfo;
    byte *ptDiskOP;
    byte *ptFileOP;
    byte *ptFileList;
    byte *ptLinkForAllLDisk;
    byte *os_mutex;
    byte *os_priv;
};

typedef struct ldiv_t ldiv_t, *Pldiv_t;

struct ldiv_t {
    byte quot;
    byte rem;
};

typedef struct LFN_ENT_T LFN_ENT_T, *PLFN_ENT_T;

struct LFN_ENT_T {
    byte ucLDirOrd;
    byte pucLDirName1[10];
    byte ucLDirAttrib;
    byte ucLDirType;
    byte ucLDirChksum;
    byte pucLDirName2[12];
    byte pucLDirFirstClusLo[2];
    byte pucLDirName3[4];
};

typedef struct lldiv_t lldiv_t, *Plldiv_t;

struct lldiv_t {
    byte quot;
    byte rem;
};

typedef enum MEDIA_TYPE_E {
    MFL_MEDIA_UNKNOWN=1000
} MEDIA_TYPE_E;

typedef struct MV_CFG_T MV_CFG_T, *PMV_CFG_T;

struct MV_CFG_T {
    byte eInMediaType;
    byte eOutMediaType;
    byte eInStrmType;
    byte eOutStrmType;
    byte eAuCodecType;
    byte eVidCodecType;
    byte *ptStrmUserFun;
    byte *suInMediaFile;
    byte *szIMFAscii;
    byte *suInMetaFile;
    byte *szITFAscii;
    byte *suOutMediaFile;
    byte *szOMFAscii;
    byte *suOutMetaFile;
    byte *szOTFAscii;
    byte uInMediaMemAddr;
    byte uInMediaMemSize;
    byte uInMetaMemAddr;
    byte uInMetaMemSize;
    byte uOutMediaMemAddr;
    byte uOutMediaMemSize;
    byte uOutMetaMemAddr;
    byte uOutMetaMemSize;
    byte bUseTempFile;
    byte uStartPlaytimePos;
    byte bStartAndPause;
    byte nClipStartTime;
    byte nClipEndTime;
    byte bDoClipVideo;
    byte bIsRecordAudio;
    byte nAuABRScanFrameCnt;
    byte nAudioPlayVolume;
    byte nAudioRecVolume;
    byte nAuRecChnNum;
    byte bIsSbcMode;
    byte eAudioPlayDevice;
    byte eAudioRecDevice;
    byte eAuRecSRate;
    byte uAuRecBitRate;
    byte uAuBuffSizeDB;
    byte uAuRecAvgBitRate;
    byte uAuRecMaxBitRate;
    byte bIsRecordVideo;
    byte nMP4VidMaxSSize;
    byte nVidPlayFrate;
    byte nVidRecFrate;
    byte nVidRecIntraIntval;
    byte sVidRecWidth;
    byte sVidRecHeight;
    byte uVidBuffSizeDB;
    byte uVidRecAvgBitRate;
    byte uVidRecMaxBitRate;
    byte *ptMvCfg);
    byte *ptMvCfg);
    byte (*au_sbc_reset_buff)(VOID);
    byte nPcmDataLen);
    byte (*au_is_sbc_ready)(VOID);
    byte *usImageHeight);
    byte usImageHeight);
    byte *puFrameSize);
    byte *pucFrameBuff);
    byte *puFrameSize);
    byte (*vid_dec_state)(VOID);
    byte *ptMvCfg);
    byte *ptMvCfg);
    byte *ptMvCfg);
    byte *data_mv;
    byte *data_info;
    byte data_play_action;
    byte data_play_param;
    byte data_rec_action;
    byte data_rec_param;
    byte *param1;
    byte *param2;
    byte *param3;
    byte *param4;
};

typedef struct MV_INFO_T MV_INFO_T, *PMV_INFO_T;

struct MV_INFO_T {
    byte uInputFileSize;
    byte uMovieLength;
    byte uPlayCurTimePos;
    byte uCreationTime;
    byte uModificationTime;
    byte eAuCodecType;
    byte uAudioLength;
    byte nAuRecChnNum;
    byte eAuRecSRate;
    byte uAuRecBitRate;
    byte uAuRecMediaLen;
    byte bIsVBR;
    byte nAuPlayChnNum;
    byte eAuPlaySRate;
    byte uAuPlayBitRate;
    byte uAuTotalFrames;
    byte uAuFramesPlayed;
    byte uAuPlayMediaLen;
    byte uAuMP4BuffSizeDB;
    byte uAuMP4AvgBitRate;
    byte uAuMP4MaxBitRate;
    byte eVidCodecType;
    byte uVideoLength;
    byte uVideoFrameRate;
    byte bIsShortHeader;
    byte usImageWidth;
    byte usImageHeight;
    byte uVidTotalFrames;
    byte uVidFramesPlayed;
    byte uVidFramesSkipped;
    byte uVidPlayMediaLen;
    byte uVidRecMediaLen;
    byte uVidMP4BuffSizeDB;
    byte uVidMP4AvgBitRate;
    byte uVidMP4MaxBitRate;
    byte nMPEG4HeaderPos;
    byte nMPEG4HeaderLen;
    byte n1stVidFramePos;
    byte n1stVidFrameLen;
    byte nMediaClipProgress;
    byte nRecDataPerSec;
    byte nMP4RecMetaReserved;
    byte nMP4RecMetaSize;
    byte nMP4RecMediaSize;
    byte tID3Tag;
    byte puVisualData[32];
    byte nLyricLenInFile;
    byte nLyricOffsetInFile;
    byte uLyricCurTimeStamp;
    byte pcLyricCur[256];
    byte uLyricNextTimeStamp;
    byte pcLyricNext[256];
    byte bIsEncrypted;
    byte nReserved1;
    byte nReserved2;
    byte nReserved3;
    byte nReserved4;
};

typedef struct OUTPUTTERMINALDESCRIPTOR OUTPUTTERMINALDESCRIPTOR, *POUTPUTTERMINALDESCRIPTOR;

struct OUTPUTTERMINALDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bTerminalID;
    byte wTerminalType;
    byte bAssocTerminal;
    byte bSourceID;
    byte iTerminal;
};

typedef struct P2LM_T P2LM_T, *PP2LM_T;

struct P2LM_T {
    byte lba;
    byte age;
};

typedef struct PARTITION_T PARTITION_T, *PPARTITION_T;

struct PARTITION_T {
    byte ucState;
    byte ucStartHead;
    byte ucStartSector;
    byte ucStartCylinder;
    byte ucPartitionType;
    byte ucEndHead;
    byte ucEndSector;
    byte ucEndCylinder;
    byte uFirstSec;
    byte uNumOfSecs;
    byte nSectorN;
    byte nHeadN;
    byte nCylinderN;
    byte uPartRecSecN;
    byte uStartSecN;
    byte uTotalSecN;
    byte nErrorCode;
    byte *ptLDisk;
    byte *ptNextPart;
};

typedef struct PDISK_T PDISK_T, *PPDISK_T;

struct PDISK_T {
    byte nDiskType;
    byte szManufacture[32];
    byte szProduct[32];
    byte szSerialNo[64];
    byte nCylinderNum;
    byte nHeadNum;
    byte nSectorNum;
    byte uTotalSectorN;
    byte nSectorSize;
    byte uDiskSize;
    byte nPartitionN;
    byte *ptPartList;
    byte nPreferDriveNo;
    byte *ptSelf;
    byte *ptDriver;
    byte *ptPDiskAllLink;
    byte *pvPrivate;
    byte *os_mutex;
    byte *os_priv;
};

typedef enum PLAY_CTRL_E {
    PLAY_CTRL_FF=0
} PLAY_CTRL_E;

typedef struct PT_REC_T PT_REC_T, *PPT_REC_T;

struct PT_REC_T {
    byte ucState;
    byte uStartHead;
    byte ucStartSector;
    byte ucStartCylinder;
    byte ucPartitionType;
    byte ucEndHead;
    byte ucEndSector;
    byte ucEndCylinder;
    byte uFirstSec;
    byte uNumOfSecs;
};

typedef struct PUDESCRIPTOR PUDESCRIPTOR, *PPUDESCRIPTOR;

struct PUDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bUnitID;
    byte bSourceID;
    byte wMaxMultiplier;
    byte bControlSize;
    byte bmControls;
    byte iProcessing;
};

typedef struct PWM_CALLBACK_T PWM_CALLBACK_T, *PPWM_CALLBACK_T;

struct PWM_CALLBACK_T {
    byte pfnPWM0CallBack;
    byte pfnCAP0CallBack;
    byte pfnPWM1CallBack;
    byte pfnCAP1CallBack;
    byte pfnPWM2CallBack;
    byte pfnCAP2CallBack;
    byte pfnPWM3CallBack;
    byte pfnCAP3CallBack;
};

typedef struct PWM_TIME_DATA_T PWM_TIME_DATA_T, *PPWM_TIME_DATA_T;

struct PWM_TIME_DATA_T {
    byte u8Mode;
    byte fFrequency;
    byte u8HighPulseRatio;
    byte bInverter;
    byte u8ClockSelector;
    byte u8PreScale;
    byte u32Duty;
};

typedef struct Q3D_CONFIG_T Q3D_CONFIG_T, *PQ3D_CONFIG_T;

struct Q3D_CONFIG_T {
    byte eQ3D_Reverb;
    byte eQ3D_OutType;
    byte eQ3D_Geometry;
};

typedef enum Q3D_GEOMETRY_T {
} Q3D_GEOMETRY_T;

typedef enum Q3D_OUTTYPE_T {
} Q3D_OUTTYPE_T;

typedef enum Q3D_REVERB_T {
    MFL_Q3D_ROOM=1
} Q3D_REVERB_T;

typedef enum REC_CTRL_E {
    REC_CTRL_PAUSE=0
} REC_CTRL_E;

typedef enum RTC_INT_SOURCE {
    RTC_ALARM_INT=1,
    RTC_TICK_INT=2,
    RTC_PSWI_INT=4,
    RTC_ALL_INT=7
} RTC_INT_SOURCE;

typedef enum RTC_TICK {
    RTC_TICK_1_SEC=0,
    RTC_TICK_1_2_SEC=1,
    RTC_TICK_1_4_SEC=2,
    RTC_TICK_1_8_SEC=3,
    RTC_TICK_1_16_SEC=4,
    RTC_TICK_1_32_SEC=5,
    RTC_TICK_1_64_SEC=6,
    RTC_TICK_1_128_SEC=7
} RTC_TICK;

typedef struct RTC_TICK_T RTC_TICK_T, *PRTC_TICK_T;

struct RTC_TICK_T {
    byte ucMode;
    byte *pfnTickCallBack;
};

typedef struct RTC_TIME_DATA_T RTC_TIME_DATA_T, *PRTC_TIME_DATA_T;

struct RTC_TIME_DATA_T {
    byte u8cClockDisplay;
    byte u8cAmPm;
    byte u32cSecond;
    byte u32cMinute;
    byte u32cHour;
    byte u32cDayOfWeek;
    byte u32cDay;
    byte u32cMonth;
    byte u32Year;
    byte *pfnAlarmCallBack;
};

typedef struct S_CHANNEL_CTRL S_CHANNEL_CTRL, *PS_CHANNEL_CTRL;

struct S_CHANNEL_CTRL {
    byte u32ChannelIndex;
    byte u8ChannelVolume;
    byte u16PAN;
    byte u8DataFormat;
    byte u16DFA;
    byte u32SrcBaseAddr;
    byte u32SrcThresholdAddr;
    byte u32SrcEndAddr;
    byte u16SrcSampleRate;
    byte u16OutputSampleRate;
};

typedef struct S_DEMO_FONT S_DEMO_FONT, *PS_DEMO_FONT;

struct S_DEMO_FONT {
    byte u32FontRectWidth;
    byte u32FontRectHeight;
    byte u32FontOffset;
    byte u32FontStep;
    byte u32FontOutputStride;
    byte u32FontInitDone;
    byte u32FontFileSize;
    byte pu32FontFileTmp;
    byte pu32FontFile;
    byte au16FontColor[3];
};

typedef struct S_DEMO_RECT S_DEMO_RECT, *PS_DEMO_RECT;

struct S_DEMO_RECT {
    byte u32StartX;
    byte u32StartY;
    byte u32EndX;
    byte u32EndY;
};

typedef struct S_DRVEDMA_CH_ADDR_SETTING S_DRVEDMA_CH_ADDR_SETTING, *PS_DRVEDMA_CH_ADDR_SETTING;

struct S_DRVEDMA_CH_ADDR_SETTING {
    byte u32Addr;
    byte eAddrDirection;
};

typedef struct S_DRVEDMA_DESCRIPT_FORMAT S_DRVEDMA_DESCRIPT_FORMAT, *PS_DRVEDMA_DESCRIPT_FORMAT;

struct S_DRVEDMA_DESCRIPT_FORMAT {
    byte u32SourceAddr;
    byte u32DestAddr;
    byte u32StrideAndByteCount;
    byte u32Offset;
    byte u32NextSGTblAddr;
};

typedef struct S_DRVEDMA_DESCRIPT_SETTING S_DRVEDMA_DESCRIPT_SETTING, *PS_DRVEDMA_DESCRIPT_SETTING;

struct S_DRVEDMA_DESCRIPT_SETTING {
    byte u32SourceAddr;
    byte eSrcDirection;
    byte u32DestAddr;
    byte eDestDirection;
    byte u32TransferByteCount;
    byte u32Stride;
    byte u32SrcOffset;
    byte u32DestOffset;
};

typedef struct S_DRVI2S_PLAY S_DRVI2S_PLAY, *PS_DRVI2S_PLAY;

struct S_DRVI2S_PLAY {
    byte u32BufferAddr;
    byte u32BufferLength;
    byte eSampleRate;
    byte eChannel;
    byte eFormat;
};

typedef struct S_DRVI2S_RECORD S_DRVI2S_RECORD, *PS_DRVI2S_RECORD;

struct S_DRVI2S_RECORD {
    byte u32BufferAddr;
    byte u32BufferLength;
    byte eSampleRate;
    byte eChannel;
    byte eFormat;
};

typedef struct S_DRVVPOST_MPULCM_CTRL S_DRVVPOST_MPULCM_CTRL, *PS_DRVVPOST_MPULCM_CTRL;

struct S_DRVVPOST_MPULCM_CTRL {
    byte bIsSyncWithTV;
    byte bIsVsyncSignalOut;
    byte bIsFrameMarkSignalIn;
    byte eSource;
    byte eType;
    byte eMPUType;
    byte eBus;
    byte psWindow;
    byte psTiming;
};

typedef struct S_DRVVPOST_MPULCM_TIMING S_DRVVPOST_MPULCM_TIMING, *PS_DRVVPOST_MPULCM_TIMING;

struct S_DRVVPOST_MPULCM_TIMING {
    byte u8CSnF2DCt;
    byte u8WRnR2CSnRt;
    byte u8WRnLWt;
    byte u8CSnF2WRnFt;
};

typedef struct S_DRVVPOST_MPULCM_WINDOW S_DRVVPOST_MPULCM_WINDOW, *PS_DRVVPOST_MPULCM_WINDOW;

struct S_DRVVPOST_MPULCM_WINDOW {
    byte u16LinePerPanel;
    byte u16PixelPerLine;
};

typedef struct S_DRVVPOST_SYNCLCM_HTIMING S_DRVVPOST_SYNCLCM_HTIMING, *PS_DRVVPOST_SYNCLCM_HTIMING;

struct S_DRVVPOST_SYNCLCM_HTIMING {
    byte u8PulseWidth;
    byte u8BackPorch;
    byte u8FrontPorch;
};

typedef struct S_DRVVPOST_SYNCLCM_POLARITY S_DRVVPOST_SYNCLCM_POLARITY, *PS_DRVVPOST_SYNCLCM_POLARITY;

struct S_DRVVPOST_SYNCLCM_POLARITY {
    byte bIsVsyncActiveLow;
    byte bIsHsyncActiveLow;
    byte bIsVDenActiveLow;
    byte bIsDClockRisingEdge;
};

typedef struct S_DRVVPOST_SYNCLCM_VTIMING S_DRVVPOST_SYNCLCM_VTIMING, *PS_DRVVPOST_SYNCLCM_VTIMING;

struct S_DRVVPOST_SYNCLCM_VTIMING {
    byte u8PulseWidth;
    byte u8BackPorch;
    byte u8FrontPorch;
};

typedef struct S_DRVVPOST_SYNCLCM_WINDOW S_DRVVPOST_SYNCLCM_WINDOW, *PS_DRVVPOST_SYNCLCM_WINDOW;

struct S_DRVVPOST_SYNCLCM_WINDOW {
    byte u16ClockPerLine;
    byte u16LinePerPanel;
    byte u16PixelPerLine;
};

typedef struct SEC_BUFF_T SEC_BUFF_T, *PSEC_BUFF_T;

struct SEC_BUFF_T {
    byte *pucData;
    byte *ptLDisk;
    byte uSectorNo;
    byte bIsDirty;
    byte nReaderCnt;
    byte jiffy;
    byte *os_owner;
    byte *os_priv;
};

typedef struct speed speed, *Pspeed;

struct speed {
    byte devnum;
    byte slow;
    byte USB_SPEED_HIGH;
};

typedef struct SPI_INFO_T SPI_INFO_T, *PSPI_INFO_T;

struct SPI_INFO_T {
    byte nPort;
    byte bIsSlaveMode;
    byte bIsClockIdleHigh;
    byte bIsLSBFirst;
    byte bIsAutoSelect;
    byte bIsActiveLow;
    byte bIsTxNegative;
    byte bIsLevelTrigger;
};

typedef struct STORAGE_DRIVER_T STORAGE_DRIVER_T, *PSTORAGE_DRIVER_T;

struct STORAGE_DRIVER_T {
    byte *);
    byte *);
    byte BOOL);
    byte *);
};

typedef struct STREAM_T STREAM_T, *PSTREAM_T;

struct STREAM_T {
    byte eStrmType;
    byte *pucMemBase;
    byte *pucMemEnd;
    byte uMemValidSize;
    byte *pucMemPtr;
    byte bIsRealocable;
    byte ucByte;
    byte ucBitRemainder;
    byte hFile;
    byte *ptStrmFun;
};

typedef struct STRM_FUN_T STRM_FUN_T, *PSTRM_FUN_T;

struct STRM_FUN_T {
    byte access);
    byte *ptStream);
    byte nSeek);
    byte *ptStream);
    byte *ptStream);
    byte bIsSkip);
    byte nCount);
    byte nCount);
    byte *ptStream);
};

typedef enum STRM_TYPE_E {
} STRM_TYPE_E;

typedef struct UARTDEV_T UARTDEV_T, *PUARTDEV_T;

struct UARTDEV_T {
    byte u32Port);
    byte pfnCallback);
    byte *uart);
    byte eIntType);
    byte u32Len);
    byte ucCh);
    byte (*UartGetChar)(void);
    byte (*UartGetChar_NoBlocking)(void);
};

typedef struct UNCOMPRESSFORMATDESCRIPTOR UNCOMPRESSFORMATDESCRIPTOR, *PUNCOMPRESSFORMATDESCRIPTOR;

struct UNCOMPRESSFORMATDESCRIPTOR {
    byte bLength;
    byte bDescriptorType;
    byte bDescriptorSubType;
    byte bFrameIndex;
    byte bNumFrameDescriptors;
    byte gudiFormat[16];
    byte bBitsPerPixel;
    byte bDefaultFrameIndex;
    byte bAspectRatioX;
    byte bAspectRatioY;
    byte bmInterlaceFlags;
    byte bCopyProtect;
};

typedef struct USB_BUS_T USB_BUS_T, *PUSB_BUS_T;

struct USB_BUS_T {
    byte busnum;
    byte devmap;
    byte *op;
    byte *root_hub;
    byte bus_list;
    byte *hcpriv;
    byte bandwidth_allocated;
    byte bandwidth_int_reqs;
    byte bandwidth_isoc_reqs;
};

typedef struct USB_CMD_T USB_CMD_T, *PUSB_CMD_T;

struct USB_CMD_T {
    byte bmRequestType;
    byte bRequest;
    byte wValue;
    byte wIndex;
    byte wLength;
};

typedef struct USB_CONFIG_DESC_T USB_CONFIG_DESC_T, *PUSB_CONFIG_DESC_T;

struct USB_CONFIG_DESC_T {
    byte bLength;
    byte bDescriptorType;
    byte wTotalLength;
    byte bNumInterfaces;
    byte bConfigurationValue;
    byte iConfiguration;
    byte bmAttributes;
    byte MaxPower;
    byte *interface;
    byte *extra;
    byte extralen;
};

typedef struct USB_DESC_HDR_T USB_DESC_HDR_T, *PUSB_DESC_HDR_T;

struct USB_DESC_HDR_T {
    byte bLength;
    byte bDescriptorType;
};

typedef struct USB_DEV_DESC_T USB_DEV_DESC_T, *PUSB_DEV_DESC_T;

struct USB_DEV_DESC_T {
    byte bLength;
    byte bDescriptorType;
    byte bcdUSB;
    byte bDeviceClass;
    byte bDeviceSubClass;
    byte bDeviceProtocol;
    byte bMaxPacketSize0;
    byte idVendor;
    byte idProduct;
    byte bcdDevice;
    byte iManufacturer;
    byte iProduct;
    byte iSerialNumber;
    byte bNumConfigurations;
};

typedef struct USB_DEV_ID_T USB_DEV_ID_T, *PUSB_DEV_ID_T;

struct USB_DEV_ID_T {
    byte match_flags;
    byte idVendor;
    byte idProduct;
    byte bcdDevice_lo;
    byte bcdDevice_hi;
    byte bDeviceClass;
    byte bDeviceSubClass;
    byte bDeviceProtocol;
    byte bInterfaceClass;
    byte bInterfaceSubClass;
    byte bInterfaceProtocol;
    byte driver_info;
};

typedef struct USB_DRIVER_T USB_DRIVER_T, *PUSB_DRIVER_T;

struct USB_DRIVER_T {
    byte *name;
    byte *id);
    byte *);
    byte driver_list;
    byte *buf);
    byte *id_table;
    byte *dev);
    byte *dev);
};

typedef struct USB_EP_DESC_T USB_EP_DESC_T, *PUSB_EP_DESC_T;

struct USB_EP_DESC_T {
    byte bLength;
    byte bDescriptorType;
    byte bEndpointAddress;
    byte bmAttributes;
    byte wMaxPacketSize;
    byte bInterval;
    byte bRefresh;
    byte bSynchAddress;
    byte *extra;
    byte extralen;
};

typedef struct USB_EP_Inf_T USB_EP_Inf_T, *PUSB_EP_Inf_T;

struct USB_EP_Inf_T {
    byte EP_Num;
    byte EP_Dir;
    byte EP_Type;
};

typedef struct USB_IF_DESC_T USB_IF_DESC_T, *PUSB_IF_DESC_T;

struct USB_IF_DESC_T {
    byte bLength;
    byte bDescriptorType;
    byte bInterfaceNumber;
    byte bAlternateSetting;
    byte bNumEndpoints;
    byte bInterfaceClass;
    byte bInterfaceSubClass;
    byte bInterfaceProtocol;
    byte iInterface;
    byte *endpoint;
    byte *extra;
    byte extralen;
};

typedef struct USB_IF_T USB_IF_T, *PUSB_IF_T;

struct USB_IF_T {
    byte *altsetting;
    byte act_altsetting;
    byte num_altsetting;
    byte max_altsetting;
    byte *driver;
    byte *private_data;
};

typedef struct USB_LIST_T USB_LIST_T, *PUSB_LIST_T;

struct USB_LIST_T {
    byte *prev;
};

typedef struct USB_OP_T USB_OP_T, *PUSB_OP_T;

struct USB_OP_T {
    byte *);
    byte *);
    byte *usb_dev);
    byte purb);
    byte purb);
};

typedef struct USB_STR_DESC_T USB_STR_DESC_T, *PUSB_STR_DESC_T;

struct USB_STR_DESC_T {
    byte bLength;
    byte bDescriptorType;
    byte wData[1];
};

typedef enum VID_CODEC_E {
} VID_CODEC_E;

typedef struct VIDEOCLASS VIDEOCLASS, *PVIDEOCLASS;

struct VIDEOCLASS {
    byte VideoClassConfig;
    byte VideoClassIADIF;
    byte VideoClassVCIF;
    byte VideoClassCSVCIF;
    byte VideoClassOutOT;
    byte VideoClassCameraIT;
    byte VideoClassPU;
    byte VideoClassEP3;
    byte VideoClassCSEP3;
    byte VideoClassVSIF;
    byte VideoClassHeader;
    byte VideoClassFormat1;
    byte VideoClassFrame_YUY2_1;
    byte VideoClassFrame_YUY2_2;
    byte VideoClassFrame_YUY2_3;
    byte VideoClassStill_UNCOMPRESS;
    byte VideoClassFormat2;
    byte VideoClassFrame_JPEG_1;
    byte VideoClassFrame_JPEG_2;
    byte VideoClassFrame_JPEG_3;
    byte VideoClassStill_JPEG;
    byte VideoClassColrMatch;
    byte VideoClassIF01;
    byte VideoClassEP01;
    byte VideoClassIF02;
    byte VideoClassEP02;
};

typedef struct VIDEOCLASS_AUDIO VIDEOCLASS_AUDIO, *PVIDEOCLASS_AUDIO;

struct VIDEOCLASS_AUDIO {
    byte VideoClassConfig;
    byte VideoClassIADIF;
    byte VideoClassVCIF;
    byte VideoClassCSVCIF;
    byte VideoClassOutOT;
    byte VideoClassCameraIT;
    byte VideoClassPU;
    byte VideoClassEP3;
    byte VideoClassCSEP3;
    byte VideoClassVSIF;
    byte VideoClassHeader;
    byte VideoClassFormat1;
    byte VideoClassFrame_YUY2_1;
    byte VideoClassFrame_YUY2_2;
    byte VideoClassFrame_YUY2_3;
    byte VideoClassStill_UNCOMPRESS;
    byte VideoClassFormat2;
    byte VideoClassFrame_JPEG_1;
    byte VideoClassFrame_JPEG_2;
    byte VideoClassFrame_JPEG_3;
    byte VideoClassStill_JPEG;
    byte VideoClassColrMatch;
    byte VideoClassIF01;
    byte VideoClassEP01;
    byte VideoClassIF02;
    byte VideoClassEP02;
    byte ch1[107];
};

typedef struct VIDEOCLASS_AUDIO_MJPEG VIDEOCLASS_AUDIO_MJPEG, *PVIDEOCLASS_AUDIO_MJPEG;

struct VIDEOCLASS_AUDIO_MJPEG {
    byte VideoClassConfig;
    byte VideoClassIADIF;
    byte VideoClassVCIF;
    byte VideoClassCSVCIF;
    byte VideoClassOutOT;
    byte VideoClassCameraIT;
    byte VideoClassPU;
    byte VideoClassEP3;
    byte VideoClassCSEP3;
    byte VideoClassVSIF;
    byte VideoClassHeader;
    byte VideoClassFormat2;
    byte VideoClassFrame_JPEG_1;
    byte VideoClassFrame_JPEG_2;
    byte VideoClassFrame_JPEG_3;
    byte VideoClassStill_JPEG;
    byte VideoClassColrMatch;
    byte VideoClassIF01;
    byte VideoClassEP01;
    byte VideoClassIF02;
    byte VideoClassEP02;
    byte ch1[107];
};

typedef struct VIDEOCLASS_AUDIO_YUV VIDEOCLASS_AUDIO_YUV, *PVIDEOCLASS_AUDIO_YUV;

struct VIDEOCLASS_AUDIO_YUV {
    byte VideoClassConfig;
    byte VideoClassIADIF;
    byte VideoClassVCIF;
    byte VideoClassCSVCIF;
    byte VideoClassOutOT;
    byte VideoClassCameraIT;
    byte VideoClassPU;
    byte VideoClassEP3;
    byte VideoClassCSEP3;
    byte VideoClassVSIF;
    byte VideoClassHeader;
    byte VideoClassFormat1;
    byte VideoClassFrame_YUY2_1;
    byte VideoClassFrame_YUY2_2;
    byte VideoClassFrame_YUY2_3;
    byte VideoClassStill_UNCOMPRESS;
    byte VideoClassColrMatch;
    byte VideoClassIF01;
    byte VideoClassEP01;
    byte VideoClassIF02;
    byte VideoClassEP02;
    byte ch1[107];
};

typedef struct VIDEOCLASS_MJPEG VIDEOCLASS_MJPEG, *PVIDEOCLASS_MJPEG;

struct VIDEOCLASS_MJPEG {
    byte VideoClassConfig;
    byte VideoClassIADIF;
    byte VideoClassVCIF;
    byte VideoClassCSVCIF;
    byte VideoClassOutOT;
    byte VideoClassCameraIT;
    byte VideoClassPU;
    byte VideoClassEP3;
    byte VideoClassCSEP3;
    byte VideoClassVSIF;
    byte VideoClassHeader;
    byte VideoClassFormat2;
    byte VideoClassFrame_JPEG_1;
    byte VideoClassFrame_JPEG_2;
    byte VideoClassFrame_JPEG_3;
    byte VideoClassStill_JPEG;
    byte VideoClassColrMatch;
    byte VideoClassIF01;
    byte VideoClassEP01;
    byte VideoClassIF02;
    byte VideoClassEP02;
};

typedef struct VIDEOCLASS_YUV VIDEOCLASS_YUV, *PVIDEOCLASS_YUV;

struct VIDEOCLASS_YUV {
    byte VideoClassConfig;
    byte VideoClassIADIF;
    byte VideoClassVCIF;
    byte VideoClassCSVCIF;
    byte VideoClassOutOT;
    byte VideoClassCameraIT;
    byte VideoClassPU;
    byte VideoClassEP3;
    byte VideoClassCSEP3;
    byte VideoClassVSIF;
    byte VideoClassHeader;
    byte VideoClassFormat1;
    byte VideoClassFrame_YUY2_1;
    byte VideoClassFrame_YUY2_2;
    byte VideoClassFrame_YUY2_3;
    byte VideoClassStill_UNCOMPRESS;
    byte VideoClassColrMatch;
    byte VideoClassIF01;
    byte VideoClassEP01;
    byte VideoClassIF02;
    byte VideoClassEP02;
};

typedef struct VIDEOSTREAMCMDDATA VIDEOSTREAMCMDDATA, *PVIDEOSTREAMCMDDATA;

struct VIDEOSTREAMCMDDATA {
    byte bmHint;
    byte bFormatIndex;
    byte bFrameIndex;
    byte dwFrameInterval;
    byte dwKeyFrameRate;
    byte wPFrameRate;
    byte wCompQuality;
    byte wCompWindowSize;
    byte wDelay;
    byte dwMaxVideoFrameSize;
    byte dwMaxPayloadTransferSize;
};

typedef struct VIDEOSTREAMSTILLCMDDATA VIDEOSTREAMSTILLCMDDATA, *PVIDEOSTREAMSTILLCMDDATA;

struct VIDEOSTREAMSTILLCMDDATA {
    byte bFormatIndex;
    byte bFrameIndex;
    byte bCompressionIndex;
    byte dwMaxVideoFrameSize;
    byte dwMaxPayloadTranferSize;
};

typedef enum WAKEUP_SOURCE_E {
    WE_GPIO=1,
    WE_RTC=2,
    WE_SDH=4,
    WE_UART=8,
    WE_UDC=16,
    WE_UHC=32,
    WE_ADC=64,
    WE_KPI=128
} WAKEUP_SOURCE_E;

typedef struct WB_UART_T WB_UART_T, *PWB_UART_T;

struct WB_UART_T {
    byte uart_no;
    byte uiFreq;
    byte uiBaudrate;
    byte uiDataBits;
    byte uiStopBits;
    byte uiParity;
    byte uiRxTriggerLevel;
};


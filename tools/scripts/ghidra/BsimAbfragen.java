// Fragt jede Funktion des aktiven Programms gegen die BSim-Datenbank der BSP-Objekte
// ab (CL-TOOL-REC-125). Aendert NICHTS am Programm; schreibt
// ghidra_projects/fid/bsim_treffer.csv.
//
// Argumente (optional, als Text, weil run_script reine Zahlen ablehnt):
//   s0.7   Mindestaehnlichkeit (Standard 0.7)
//   k10    Treffer je Funktion (Standard 5)
//
// Positivkontrolle: fmiInitSDDevice muss an 0x000A9184 erscheinen -- die Funktion, deren
// Ende bei 0x000A964C CL-USB-REC-119 mit SDGlue.c:541-570 gleichsetzt.
//
//@category ZK-Inkjet

import java.io.File;
import java.io.PrintWriter;
import java.net.URL;
import java.util.*;

import ghidra.app.script.GhidraScript;
import ghidra.features.bsim.query.*;
import ghidra.features.bsim.query.description.*;
import ghidra.features.bsim.query.protocol.*;
import ghidra.program.model.listing.Function;

public class BsimAbfragen extends GhidraScript {

	private static final long KONTROLLE = 0x000A9184L;   // Funktionsanfang; 0xA964C ist ihr Ende
	private static final String KONTROLL_NAME = "fmiInitSDDevice";

	@Override
	public void run() throws Exception {
		double schwelle = 0.7;
		int jeFunktion = 5;
		for (String a : getScriptArgs()) {
			if (a.startsWith("s")) {
				schwelle = Double.parseDouble(a.substring(1));
			}
			else if (a.startsWith("k")) {
				jeFunktion = Integer.parseInt(a.substring(1));
			}
		}
		// Skript liegt in <repo>/tools/scripts/ghidra/ -- drei Ebenen hoch ist das Repository.
		String repo = getSourceFile().getParentFile().getParentFile().getParentFile()
				.getParentFile().getAbsolutePath();
		File fid = new File(new File(repo, "ghidra_projects"), "fid");
		File db = new File(fid, "bsim_bsp");
		if (!new File(fid, "bsim_bsp.mv.db").exists()) {
			throw new IllegalStateException("Keine BSim-Datenbank unter " + db);
		}
		URL url = BSimClientFactory.deriveBSimURL("file:" + db.getAbsolutePath());

		try (FunctionDatabase datenbank = BSimClientFactory.buildClient(url, false)) {
			if (!datenbank.initialize()) {
				throw new IllegalStateException(datenbank.getLastError().message);
			}
			GenSignatures gensig = new GenSignatures(false);
			try {
				gensig.setVectorFactory(datenbank.getLSHVectorFactory());
				gensig.openProgram(currentProgram, null, null, null, null, null);
				int anzahl = currentProgram.getFunctionManager().getFunctionCount();
				gensig.scanFunctions(currentProgram.getFunctionManager().getFunctions(true), anzahl,
					monitor);

				QueryNearest q = new QueryNearest();
				q.manage = gensig.getDescriptionManager();
				q.max = jeFunktion;
				q.thresh = schwelle;
				q.signifthresh = 0.0;
				ResponseNearest antwort = q.execute(datenbank);
				if (antwort == null) {
					throw new IllegalStateException(datenbank.getLastError().message);
				}

				File csv = new File(fid, "bsim_treffer.csv");
				int mitTreffer = 0, eindeutig = 0;
				String kontrolle = "nicht unter den Treffern";
				TreeMap<String, Integer> jeObjekt = new TreeMap<>();
				try (PrintWriter w = new PrintWriter(csv, "UTF-8")) {
					w.println("va,name_jetzt,bester_name,objekt,aehnlichkeit,signifikanz,namen_ueber_schwelle");
					for (SimilarityResult r : antwort.result) {
						FunctionDescription basis = r.getBase();
						long va = basis.getAddress();
						SimilarityNote beste = null;
						TreeSet<String> namen = new TreeSet<>();
						for (Iterator<SimilarityNote> it = r.iterator(); it.hasNext();) {
							SimilarityNote n = it.next();
							namen.add(n.getFunctionDescription().getFunctionName());
							if (beste == null || n.getSimilarity() > beste.getSimilarity()) {
								beste = n;
							}
						}
						if (beste == null) {
							continue;
						}
						mitTreffer++;
						if (namen.size() == 1) {
							eindeutig++;
						}
						FunctionDescription b = beste.getFunctionDescription();
						String obj = b.getExecutableRecord().getNameExec();
						jeObjekt.merge(obj, 1, Integer::sum);
						w.printf("0x%08X,%s,%s,%s,%.3f,%.1f,%s%n", va, basis.getFunctionName(),
							b.getFunctionName(), obj, beste.getSimilarity(), beste.getSignificance(),
							String.join("|", namen));
						if (va == KONTROLLE) {
							kontrolle = String.format("%s (%.3f), alle Namen: %s", b.getFunctionName(),
								beste.getSimilarity(), namen);
						}
					}
				}
				println(String.format("Schwelle %.2f, %d Funktionen abgefragt, %d mit Treffer, %d mit nur einem Namen",
					schwelle, anzahl, mitTreffer, eindeutig));
				println(String.format("KONTROLLE 0x%08X (%s): %s", KONTROLLE, KONTROLL_NAME, kontrolle));
				println("Treffer je Objekt (bester Treffer, Auszug):");
				jeObjekt.entrySet().stream()
						.sorted((x, y) -> y.getValue() - x.getValue())
						.limit(30)
						.forEach(e -> println(String.format("   %-36s %d", e.getKey(), e.getValue())));
				println("CSV: " + csv);
			}
			finally {
				gensig.dispose();
			}
		}
	}
}

// Baut eine Function-ID-Datenbank aus den importierten BSP-Objekten (CL-TOOL-REC-123).
//
// Erwartet im aktiven Projekt einen Ordner, dessen Unterordner je eine Bibliothek
// sind (so legt build_bsp_fid.sh sie an). Jeder Unterordner wird eine Bibliothek in
// der .fidb, Name = Ordnername. Laeuft headless, ohne Dialoge:
//
//   analyzeHeadless <proj> <name> -process <irgendein Programm> -noanalysis -readOnly \
//       -scriptPath tools/scripts/ghidra \
//       -postScript BuildBspFid.java <ausgabe.fidb> <wurzelordner> <version> <variante>
//
// Die Ausgabedatei darf nicht existieren -- das Skript ueberschreibt nichts.
//
//@category ZK-Inkjet

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map.Entry;

import ghidra.app.script.GhidraScript;
import ghidra.feature.fid.db.FidDB;
import ghidra.feature.fid.db.FidFile;
import ghidra.feature.fid.db.FidFileManager;
import ghidra.feature.fid.service.FidPopulateResult;
import ghidra.feature.fid.service.FidPopulateResult.Disposition;
import ghidra.feature.fid.service.FidService;
import ghidra.framework.model.DomainFile;
import ghidra.framework.model.DomainFolder;
import ghidra.program.database.ProgramContentHandler;
import ghidra.program.model.lang.LanguageID;

public class BuildBspFid extends GhidraScript {

	private static final String SPRACHE = "ARM:LE:32:v5t";

	private void programme(DomainFolder ordner, List<DomainFile> liste) {
		for (DomainFile f : ordner.getFiles()) {
			if (f.getContentType().equals(ProgramContentHandler.PROGRAM_CONTENT_TYPE)) {
				liste.add(f);
			}
		}
		for (DomainFolder u : ordner.getFolders()) {
			programme(u, liste);
		}
	}

	@Override
	protected void run() throws Exception {
		String[] a = getScriptArgs();
		if (a.length != 4) {
			throw new IllegalArgumentException(
				"Argumente: <ausgabe.fidb> <wurzelordner> <version> <variante>");
		}
		File ausgabe = new File(a[0]);
		if (ausgabe.exists()) {
			throw new IllegalStateException(ausgabe + " existiert schon. Abbruch.");
		}
		DomainFolder wurzel = getProjectRootFolder().getFolder(a[1]);
		if (wurzel == null) {
			throw new IllegalStateException("Ordner /" + a[1] + " fehlt im Projekt.");
		}

		FidFileManager fm = FidFileManager.getInstance();
		fm.createNewFidDatabase(ausgabe);
		FidFile fidFile = fm.addUserFidFile(ausgabe);
		FidDB db = fidFile.getFidDB(true);
		FidService svc = new FidService();
		LanguageID sprache = new LanguageID(SPRACHE);

		int summeBesucht = 0, summeAufgenommen = 0, bibliotheken = 0;
		try {
			for (DomainFolder lib : wurzel.getFolders()) {
				monitor.checkCancelled();
				List<DomainFile> progs = new ArrayList<>();
				programme(lib, progs);
				if (progs.isEmpty()) {
					continue;
				}
				FidPopulateResult r = svc.createNewLibraryFromPrograms(db, lib.getName(), a[2],
					a[3], progs, null, sprache, null, null, monitor);
				if (r == null) {
					println(String.format("%-40s keine Funktionen", lib.getName()));
					continue;
				}
				bibliotheken++;
				summeBesucht += r.getTotalAttempted();
				summeAufgenommen += r.getTotalAdded();
				StringBuilder aus = new StringBuilder();
				for (Entry<Disposition, Integer> e : r.getFailures().entrySet()) {
					if (e.getKey() != Disposition.INCLUDED) {
						aus.append(' ').append(e.getKey()).append('=').append(e.getValue());
					}
				}
				println(String.format("%-40s %3d Objekte  %4d besucht  %4d aufgenommen %s",
					lib.getName(), progs.size(), r.getTotalAttempted(), r.getTotalAdded(), aus));
			}
			db.saveDatabase("BSP-FID", monitor);
		}
		finally {
			db.close();
		}
		println(String.format("SUMME: %d Bibliotheken, %d Funktionen besucht, %d aufgenommen -> %s",
			bibliotheken, summeBesucht, summeAufgenommen, ausgabe));
	}
}

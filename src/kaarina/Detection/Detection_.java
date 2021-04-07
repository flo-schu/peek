import ij.IJ;
import ij.ImagePlus;
import ij.WindowManager;
import ij.gui.GenericDialog;
import ij.io.FileSaver;
import ij.io.SaveDialog;
import ij.measure.Measurements;
import ij.measure.ResultsTable;
import ij.plugin.PlugIn;
import ij.plugin.filter.Analyzer;
import ij.plugin.filter.ParticleAnalyzer;
import ij.process.Blitter;
import ij.process.ImageProcessor;
import ij.text.TextWindow;

import java.awt.Button;
import java.awt.FlowLayout;
import java.awt.Panel;
import java.awt.TextField;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FilenameFilter;
import java.util.Vector;




public class Detection_ implements PlugIn, Measurements, ActionListener {

	
	/** Display results in the ImageJ console. */
	public static final int SHOW_RESULTS = 1, SHOW_OUTLINES = 4, MIN =12, SHOW_SIZE_DISTRIBUTION = 16, DIFFERENCE=8, COPY=0;
	public static final int SHOW_PROGRESS = 32, CLEAR_WORKSHEET = 64, RECORD_STARTS = 128,DISPLAY_SUMMARY = 256, SHOW_NONE = 512;
	public static final int MAJOR = 15, MINOR = 16, BLACK = -16777216, GET_BOUNDS = 375,RED_LUT=0;
	protected static final int NOTHING=0,OUTLINES=1,MASKS=2,ELLIPSES=3;
		
	
	ResultsTable rt = new ResultsTable();
	ImagePlus impOrig, impLayer, impColl, impSez, impTeile, imps, imps2, imps_ha, imp0, imp1, imp2;
	ImageProcessor ipOrig, ipLayer, ipColl, ipSez, ipTeile, ips, ips2, ips_, ip0, ip1, ip2; 
	int w,h, wGr, hGr;
	int repli;
	int measurements,options;
	double weiss = 65535;
	GenericDialog gd;
	Button browse1, browse2;
	String species,method;
	boolean color;
	double start=0, end=149;
//	double thr;
	int anzFotos=0;
	String bild;
	float[][]gross,lang,breit,hell;//Ergebnistabellen für Daphnien
	int[][]resImmo, resMobil,bioImmo,bioMobil;//Ergebnistabellen für Culexlarven
	String XXdaph1 ="",XXdaph2="",XXculex1="",XXculex2="",XXculex3="",XXculex4="";
	
	static String path = "";
	
	
	
//	--------------------------------------------------------------------------------------
	
	public void run(String arg) {
		
		measurements = Analyzer.getMeasurements(); // defined in Set Measurements dialog
		Analyzer.setMeasurements(0);
		measurements |= AREA+PERIMETER+ELLIPSE+CIRCULARITY+MEAN;;  //make sure area is measured
		options = CLEAR_WORKSHEET+RECORD_STARTS;//+SHOW_NONE;
		Analyzer.setMeasurements(measurements);
		ParticleAnalyzer pa = new ParticleAnalyzer(options, measurements, rt, 0, 99999999);
	
		
		getData();//User sagt über Maske, was er will...
		
		
		File ordner = new File(path);
		FilenameFilter filter1 = new FilenameFilter(){
	          public boolean accept(File ordner, String messung){
	              return messung.startsWith("#");}};//nur die Messtermine sollen abgearbeitet werden
	     		
		String[] termine = ordner.list(filter1);
		
	
	
	
	//############################################################################################
		      

		XXdaph1 = "Xd1 ";
		XXdaph2 = "Xd2 ";
		XXculex1= "Xc1 ";
		XXculex2= "Xc2 ";
		XXculex3= "Xc3 ";
		XXculex4= "Xc4 ";

 
	
	if(species=="Daphnia"){
  
	
	for (int qq=0; qq<termine.length; qq++) {//die größte Schleife zum abarbeiten aller Ordner
	      String tag = termine[qq];
	     
	    anzFotos=(int)(end-start+1); 
	  	gross=new float [anzFotos][4000];//Ergebnistabellen	
	  	lang=new float [anzFotos][4000];	
	  	breit=new float [anzFotos][4000];	
 
	      
  for (int zz=(int)start; zz<=(int)end; zz=zz+3){ 
					
		System.out.println(IJ.currentMemory()); 
		int min_freeMemory = 50;
		int freeMemory;
		for (int i=0; i<100; i++) {
        System.gc();// run garbage collector:
		freeMemory = 100 - (int)(IJ.currentMemory() * 100 / IJ.maxMemory());// MemoryCheck:
		if (freeMemory >= min_freeMemory) {
		break;}}
		System.out.println(IJ.currentMemory());	
			
	    IJ.open(path + "\\" +tag+ "\\" + zz + ".jpg");
		impOrig  = WindowManager.getImage(zz + ".jpg");
		impOrig.setTitle("0");
		ipOrig=impOrig.getProcessor();
		wGr = impOrig.getWidth();
		hGr = impOrig.getHeight();
		    
		if(ipOrig.get(0, 0)==255){
		impOrig.unlock();
		impOrig.changes = false;
		impOrig.close();}
		else{
				    
		ipOrig.max(254);//nichts ist weiß!!	
	    impOrig.setProcessor(null,ipOrig);
		IJ.open(path + "\\" +tag+ "\\" + (zz+1) + ".jpg");
		WindowManager.getImage((zz+1) + ".jpg").setTitle("1");
		IJ.open(path + "\\" +tag+ "\\" + (zz+2) + ".jpg");
		WindowManager.getImage((zz+2) + ".jpg").setTitle("2");
		

		//IJ.run("Xdaph1 Camera1 ");//Oberer Rand wird gefunden und entfernt
		IJ.run(XXdaph1);//Oberer Rand wird gefunden und entfernt
		IJ.run(XXdaph2);//Detektion der Daphnien

				

		if (WindowManager.getImageCount()==0){}	else {
		for (int i =0; i<3; i++){ //die drei Fotos einzeln abarbeiten
		
			imps  = WindowManager.getImage(""+i);
			imps2  = WindowManager.getImage("o"+i);
			rt.reset();
			pa.analyze(imps);
			messungD (rt, imps, gross, lang, breit, zz-(int)start+i);
			
			new FileSaver(imps).saveAsPng(path+ "\\" +tag+ "\\sw_" + (zz+i) + ".png");
			new FileSaver(imps2).saveAsPng(path+ "\\" +tag+ "\\flöhe_" + (zz+i) + ".png");
			imps.unlock();	
			imps.changes = false;
			imps.close();
			imps2.unlock();
			imps2.changes = false;
			imps2.close();
					
		}}
	}}
		writeResultsD(gross,lang,breit,tag);
	}	
 }			
			
		
//#########################################################################################		
	
		if(species=="Culex"){//wenn die Mücken detektiert werden sollen!!
 	      
			
		for (int qq=0; qq<termine.length; qq++) {//die größte Schleife zum abarbeiten aller Ordner
		      String tag = termine[qq];
		
		//Ergebnistabelle
		anzFotos=(int)(end-start+1);      
		resImmo=new int [anzFotos/3][3000];
		resMobil=new int [anzFotos][3000];
		bioImmo=new int [2][anzFotos/3];
		bioMobil=new int [2][anzFotos];      
		
		
		
		for (int zz=(int)start; zz<=(int)end; zz=zz+3){ 
		
		System.out.println(IJ.currentMemory()); 
		int min_freeMemory = 50;
		int freeMemory;
		for (int i=0; i<100; i++) {
        System.gc();// run garbage collector:
		freeMemory = 100 - (int)(IJ.currentMemory() * 100 / IJ.maxMemory());// MemoryCheck:
		if (freeMemory >= min_freeMemory) {
		break;}}
		System.out.println(IJ.currentMemory());	
			
			
		IJ.open(path + "\\" +tag+ "\\" + zz + ".jpg");
		impOrig  = WindowManager.getImage(zz + ".jpg");
		impOrig.setTitle("0");
		ipOrig=impOrig.getProcessor();
		wGr = impOrig.getWidth();
		hGr = impOrig.getHeight();
		    
		if(ipOrig.get(0, 0)==255){
		impOrig.unlock();
		impOrig.changes = false;
		impOrig.close();}
		else{
					    
		ipOrig.max(254);//nichts ist weiß!!	
		impOrig.setProcessor(null,ipOrig);
		IJ.open(path + "\\" +tag+ "\\" + (zz+1) + ".jpg");
		WindowManager.getImage((zz+1) + ".jpg").setTitle("1");
		IJ.open(path + "\\" +tag+ "\\" + (zz+2) + ".jpg");
		WindowManager.getImage((zz+2) + ".jpg").setTitle("2");
		
		
		IJ.run(XXculex1);
     	IJ.run(XXculex2); //Biomasse herausschälen und einfach sklelettieren
		IJ.run(XXculex3); //weitere Behandlung der Skelette
		IJ.run(XXculex4); //Analyse der beweglichen Larven
		
		
//		------------------------------------------------------------------------------------------		
//		Ausmessung der Immobilen Larven	
				
		impSez  = WindowManager.getImage("sez.png");
		ipSez=impSez.getProcessor();
		ipSez=ipSez.rotateLeft();
		impSez.setProcessor(null, ipSez);
		w = ipSez.getWidth(); //x-werte
		h = ipSez.getHeight(); //y-werte
		impColl  = WindowManager.getImage("Coll");
		ipColl=impColl.getProcessor();
		ipColl=ipColl.rotateLeft();
		impColl.setProcessor(null, ipColl);
		impTeile  = WindowManager.getImage("Teile");
		ipTeile=impTeile.getProcessor();
		ipTeile=ipTeile.rotateLeft();
		impTeile.setProcessor(null, ipTeile);
		
		int max=0;
		for(int y=0;y<h;y++){
		for(int x=0;x<w;x++){
		if(ipTeile.getPixel(x,y)<weiss){
		max=Math.max(max, ipTeile.getPixel(x,y));}}}
		int []area= new int [max+1];//Einmal durchzählen - wieviele Objekte habe ich 
		
				
		//Pixelzählung!!
		for(int y=0;y<h;y++){
		for(int x=0;x<w;x++){
		if(ipTeile.getPixel(x,y)<weiss){
		area[ipTeile.getPixel(x,y)]++;}}}//Pixel werden gezählt
		
		//Übertragung in Resulttabelle
		int count=0;
		for(int i=0; i<=max; i++){
		if(area[i]>0){
		resImmo[(zz-(int)start)/3][count]=area[i];
		count++;}}
		
		
		//Bilder speichern
		new FileSaver(impSez).saveAsPng(path +"\\" +tag+ "\\bio_" +zz+ ".png");
		new FileSaver(impColl).saveAsPng(path +"\\" +tag+ "\\entf_" +zz+ ".png");
		//Teile in Coll übertragen und als 8-bit abspeichern
		ipColl.resetRoi();
		ipColl.min(255);
		for(int y=0;y<h;y++){
		for(int x=0;x<w;x++){
				if(ipTeile.getPixel(x,y)<weiss){
				ipColl.set(x, y, (int)Math.IEEEremainder(ipTeile.getPixel(x,y), 250));}}}
		impColl.setProcessor(null, ipColl);
		new FileSaver(impColl).saveAsPng(path +"\\" +tag+ "\\skelett_" +zz+ ".png");
		

		//Skelette im Biomassebild rot einfärben und abspeichern 
		impSez  = WindowManager.getImage("viele.png");
		ipSez=impSez.getProcessor();
		ipSez=ipSez.rotateLeft();
		ipSez.min(1);//	schwarze Fläche in Sez auf 1 setzen
		impSez.setProcessor(null,ipSez);	
		IJ.selectWindow("Teile");
		IJ.run("8-bit");
		IJ.setThreshold(0,254);	
		IJ.run("Convert to Mask");
		IJ.run("Invert LUT");
		IJ.run("Invert");
		ipTeile=impTeile.getProcessor();
		ipSez.copyBits(ipTeile, 0, 0, Blitter.MIN);
		impSez.setProcessor(null,ipSez);
		IJ.selectWindow("viele.png");
		IJ.setThreshold(0,0);
		IJ.run("RGB Color");
		new FileSaver(impSez).saveAsPng(path +"\\" +tag+ "\\kontr_" +zz + ".png");

		//alles schließen		
		impTeile.unlock();
		impTeile.changes = false;
		impTeile.close();
		impSez.unlock();
		impSez.changes = false;
		impSez.close();
		impColl.unlock();
		impColl.changes = false;
		impColl.close();
		ImagePlus imp = WindowManager.getImage("sez.png");
		imp.unlock();
		imp.changes = false;
		imp.close();
		}
		
//		------------------------------------------------------------------------------------------		
//		------------------------------------------------------------------------------------------		
//		Ausmessung der mobilen Larven	
		
		//sind noch Fenster geöffnet??
		if (WindowManager.getImageCount()==0){}
		else {
		String[] names1 = {"0","1", "2"};
		pa = new ParticleAnalyzer(options, measurements, rt, 0, 99999999);
		
		for (int s=0;s<3;s++){
		imps  = WindowManager.getImage(names1[s]);
		ips = imps.getProcessor();
		
		IJ.selectWindow(names1[s]);
		IJ.run("Skeletonize");
			
		rt.reset();
		pa.analyze(imps);
		int anz=rt.getCounter();
		float[] a = rt.getColumn(ResultsTable.AREA);
		for(int ii=0; ii<anz;ii++){
		resMobil[zz-(int)start+s][ii]=(int)a[ii];}
		
		new FileSaver(imps).saveAsPng(path + "\\" +tag+ "\\Mskelett_" +(zz+s)+ ".png");
		imps.unlock();
		imps.changes = false;
		imps.close();
		ips.reset();
		

	    }}
		}
		writeResults(resImmo, tag, "#AbundImmo");
		writeResults(resMobil, tag, "#AbundMobil");
}}		
		

}

		
		
    void getData(){
	    gd = new GenericDialog("Settings");
	    
	    String[] choices = {"","Daphnia", "Culex"};
	    gd.addChoice("Species: ", choices, "");
	    gd.addMessage("");
	    
//		gd.showDialog();
//	    addition florian to create new field for daphnia
//	    if (species == "Daphnia"){
//			gd.addMessage("Enter threshold for Daphnia detection size");
//	    	gd.addNumericField("threshold:",45,0);
//			gd.addMessage("");
//	    } else {
//	    	gd.addMessage("Error");
//	    }

		gd.addStringField("Path to the image folders (# + date):", path, 30);
		gd.addPanel(makePanel(gd, 2));
		gd.addMessage("");
	
		gd.addMessage("Detection:");
		gd.addNumericField("from image:", 0, 0);
		gd.addNumericField("to image:", 149, 0);
				    	
		gd.showDialog();
		
		species = gd.getNextChoice();
		path = gd.getNextString();
//		thr = gd.getNextNumber();
		start = gd.getNextNumber();
		end = gd.getNextNumber();
		
			
	    }

      
    
	Panel makePanel(GenericDialog gd, int id) {
		Panel panel = new Panel();
		panel.setLayout(new FlowLayout(FlowLayout.RIGHT, 0, 0));
			browse1 = new Button("Browse...");
			browse1.addActionListener(this);
			panel.add(browse1);
		return panel;
	}



	void getDir() {
		SaveDialog sd = new SaveDialog("Open destination folder...", "dummy name (required)", "");
		if (sd.getFileName()==null)
			return;
		Vector stringField = gd.getStringFields();
		TextField tf = (TextField)(stringField.elementAt(0));
		tf.setText(sd.getDirectory());
	}


	public void actionPerformed(ActionEvent e) {
		Object source = e.getSource();
		if (source==browse1)
			getDir();
	}		


	void writeResults(int[][]results, String tag, String Bez){
		
		int sp = results.length;
		int teiler=anzFotos/sp;
		String headings = "";
		String aLine = "";
		
		for (int i = (int)start; i <= (int)end; i=i+teiler){
			headings += i + "\t";
		}
			
		TextWindow mtw = new TextWindow("Ergebnisse", headings, aLine, 550, 180);//erstmal Tabelle öffnen
		for(int ze=0; ze< 3000; ze++){
		for(int sl=0; sl< sp; sl++){
				aLine += IJ.d2s(results[sl][ze],0)+"\t";
				}
		mtw.append(aLine);
		aLine = "";
		}
		
		IJ.selectWindow("Ergebnisse");
		IJ.saveAs("Text", path+"\\" +tag+ "\\" +Bez+ ".txt");
		IJ.run("Text...", "save=["+ path+ "\\" +tag+ "\\" +Bez+ ".txt]");
		mtw.dispose();
		mtw.close();
	
		
	}	
	
	void writeBiomasse(int zeilen, int[][]biomasse, String tag, String Bez){
		
		String headings = "Foto" +"\t" +"Gesamt";
		String aLine = "";
						
		TextWindow mtw = new TextWindow("Biomasse", headings, aLine, 550, 180);//erstmal Tabelle öffnen
		for(int ze=0; ze< zeilen; ze++){
			aLine=""+biomasse[0][ze] +"\t" + biomasse[1][ze];
		mtw.append(aLine);}
		
		IJ.selectWindow("Biomasse");
		IJ.saveAs("Text", path+"\\" +tag+ "\\" +Bez+ ".txt");
		IJ.run("Text...", "save=["+ path+ "\\" +tag+ "\\" +Bez+ ".txt]");
		mtw.dispose();
		mtw.close();
	
		
	}

	void messungD (ResultsTable rt, ImagePlus imp, float [][]gross, float [][]lang, float [][]breit, int nr){
		int anz = rt.getCounter();
		if (anz == 0)
			return;
		
		float [] g = rt.getColumn(ResultsTable.AREA);
		float [] l = rt.getColumn(ResultsTable.MAJOR);
		float [] b = rt.getColumn(ResultsTable.MINOR);

		for (int i=0; i<anz;i++){
		gross[nr][i]=g[i];
		lang[nr][i]=l[i];
		breit[nr][i]=b[i];
		}
	}



	void writeResultsD(float [][]gross, float [][]lang, float [][]breit, String tag){
			
		int spalten = gross.length;
		String headings = "";
		String aLine = "";
		
		for (int i = (int)start; i <= (int)end; i++){
			headings += i + "\t";
		}	
		

				
			TextWindow mtwG = new TextWindow("Erg_gross", headings, aLine, 550, 180);//erstmal Tabelle öffnen
			for(int ze=0; ze< 4000; ze++){
			for(int sl=0; sl< spalten; sl++){
					aLine += IJ.d2s(gross[sl][ze],0)+"\t";
					}
			mtwG.append(aLine);
			aLine = "";
			}
			
			TextWindow mtwL = new TextWindow("Erg_lang", headings, aLine, 550, 180);//erstmal Tabelle öffnen
			for(int ze=0; ze< 4000; ze++){
			for(int sl=0; sl< spalten; sl++){
					aLine += IJ.d2s(lang[sl][ze],1)+"\t";
					}
			mtwL.append(aLine);
			aLine = "";
			}
			
			TextWindow mtwB = new TextWindow("Erg_breit", headings, aLine, 550, 180);//erstmal Tabelle öffnen
			for(int ze=0; ze< 4000; ze++){
			for(int sl=0; sl< spalten; sl++){
					aLine += IJ.d2s(breit[sl][ze],1)+"\t";
					}
			mtwB.append(aLine);
			aLine = "";
			}

				
			
			IJ.selectWindow("Erg_gross");
			IJ.saveAs("Text", path+ "\\" +tag+ "\\Erg_gross.txt");
			IJ.run("Text...", "save=["+path+ "\\" +tag+ "\\Erg_gross.txt]");
			mtwG.dispose();
			mtwG.close();
			
			IJ.selectWindow("Erg_lang");
			IJ.saveAs("Text", path+ "\\" +tag+ "\\Erg_lang.txt");
			IJ.run("Text...", "save=["+path+ "\\" +tag+ "\\Erg_lang.txt]");
			mtwL.dispose();
			mtwL.close();
			
			IJ.selectWindow("Erg_breit");
			IJ.saveAs("Text", path+ "\\" +tag+ "\\Erg_breit.txt");
			IJ.run("Text...", "save=["+path+ "\\" +tag+ "\\Erg_breit.txt]");
			mtwB.dispose();
			mtwB.close();

			
		}
	
	
}




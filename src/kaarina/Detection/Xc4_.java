import ij.ImagePlus;
import ij.WindowManager;
import ij.gui.PolygonRoi;
import ij.gui.Roi;
import ij.gui.Wand;
import ij.measure.Measurements;
import ij.measure.ResultsTable;
import ij.plugin.PlugIn;
import ij.plugin.filter.Analyzer;
import ij.plugin.filter.EDM;
import ij.plugin.filter.MaximumFinder;
import ij.plugin.filter.ParticleAnalyzer;
import ij.process.Blitter;
import ij.process.ByteProcessor;
import ij.process.ImageProcessor;




public class Xc4_ implements PlugIn, Measurements {

public static final int SHOW_RESULTS = 1, SHOW_OUTLINES = 4, MIN =12, SHOW_SIZE_DISTRIBUTION = 16, DIFFERENCE=8, COPY=0;
public static final int SHOW_PROGRESS = 32, CLEAR_WORKSHEET = 64, RECORD_STARTS = 128,DISPLAY_SUMMARY = 256, SHOW_NONE = 512;
public static final int MAJOR = 15, MINOR = 16, BLACK = -16777216, GET_BOUNDS = 375,RED_LUT=0;
protected static final int NOTHING=0,OUTLINES=1,MASKS=2,ELLIPSES=3;


ResultsTable rt = new ResultsTable();
ImagePlus imp0, imp1, imp2, imps, imps2;
ImageProcessor ip0, ip1, ip2, ip0a, ip1a, ip2a, ip, ips, ips2, ips_;
ByteProcessor bp;
int w,h;
int measurements,options;
int unten;
int thr=45;
int boden =0;//ist bereits entfernt worden, nicht nochmal extra berücksichtigen...
int daph;

public void run(String arg) {

measurements = Analyzer.getMeasurements(); // defined in Set Measurements dialog
Analyzer.setMeasurements(0);
measurements |= AREA+PERIMETER+ELLIPSE+CIRCULARITY+MEAN+FERET;;  //make sure area is measured
options = CLEAR_WORKSHEET+RECORD_STARTS;//+SHOW_NONE;
Analyzer.setMeasurements(measurements);
ParticleAnalyzer pa = new ParticleAnalyzer(options, measurements, rt, 0, 99999999);


	imp0  = WindowManager.getImage("0");
	ip0a = imp0.getProcessor();
	imp1  = WindowManager.getImage("1");
	ip1a = imp1.getProcessor().convertToByte(false);
	imp1.setProcessor(null,ip1a);
	imp2  = WindowManager.getImage("2");
	ip2a = imp2.getProcessor().convertToByte(false);
	imp2.setProcessor(null,ip2a);
	

	
	//wenn dummie, dann break
	if(ip2a.get(0, 0)==255)	{
	imp0.unlock();
	imp0.changes = false;
	imp0.close();
	imp1.unlock();
	imp1.changes = false;
	imp1.close();
	imp2.unlock();
	imp2.changes = false;
	imp2.close();}
	
	else {
	unten=200;//was unten ab

	//mit dieser Größe neue Prozessoren bilden und Bilder hineinkopieren
	ip0 = ip0a.createProcessor(imp0.getWidth()-unten,imp0.getHeight());
	ip1 = ip1a.createProcessor(imp0.getWidth()-unten,imp0.getHeight());
	ip2 = ip2a.createProcessor(imp0.getWidth()-unten,imp0.getHeight());
	ip0.copyBits(ip0a, -unten, 0, COPY);
	imp0.setProcessor(null,ip0);
	ip1.copyBits(ip1a, -unten, 0, COPY);
	imp1.setProcessor(null,ip1);
	ip2.copyBits(ip2a, -unten, 0, COPY);
	imp2.setProcessor(null,ip2);
			
	
	//-------------------------------------------------------------------------------------------------
	//Fotos voneinander abziehen
	ip = ip0.duplicate();
	ip.copyBits(ip1, 0, 0, Blitter.MIN);
	ip.copyBits(ip2, 0, 0, Blitter.MIN);
	imp1.setProcessor(null,ip);
	//new FileSaver(imp1).saveAsPng(pfad + "\\" +tag+ "\\" +fotoNr+ "back.png");
	ip0.copyBits(ip, 0, 0, Blitter.DIFFERENCE);
	imp0.setProcessor(null,ip0);
	ip1.copyBits(ip, 0, 0, Blitter.DIFFERENCE);
	imp1.setProcessor(null,ip1);
	ip2.copyBits(ip, 0, 0, Blitter.DIFFERENCE);
	imp2.setProcessor(null,ip2); //hat geklappt
	w=imp0.getWidth();
	h=imp0.getHeight();
	
//-----------------------------------------------------------------------------------------
	//Fotos per Schleife hintereinander abarbeiten
	
		
	for (int s=0;s<3;s++){
		if (s == 0)
		{ips = ip0.duplicate();	 imps=imp0; }
		if (s == 1)
		{ips = ip1.duplicate();	 imps=imp1; }				
		if (s == 2)
		{ips = ip2.duplicate();	 imps=imp2; }	
			
		
				
		//zum Binärbild umformen
		thr=40;//auch für später
		ips.threshold(thr);//Original als binär
		ips.invert();
		imps.setProcessor(null,ips);	
		
		
		//splitten und glätten
		//imps.setProcessor(null,ips);
		ips.erode();
		ips.erode();
		ips.dilate();
		ips.dilate();
		imps.setProcessor(null,ips);
		
		
				
		//damit es schneller geht, schonmal alle eindeutigen Daphnien entfernen 
		int floh = 20;//Mindestgröße für Larven
		rt.reset();
		pa.analyze(imps);
		//xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
		daph = rundDmitCweg (rt,ips,floh,boden);//zusätzlich: Larven weg!!
		//xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
		imps.setProcessor(null,ips);
		
		if(daph>250){//also wenn soviel Daphnien da sind, dass eine Überlappung überhaupt möglich ist... (bzw. 2 Daphnien eine Mücke bilden können)
		//was übrig bleibt nachbearbeiten mit superleichtem Watershedding, daher zu Fuß
		EDM edm = new EDM();
		ips.invert();
	    imps.setProcessor(null, ips);
	    ImageProcessor ipfloat=edm.makeFloatEDM(ips, 0, false);
	    imps.setProcessor(null, ipfloat);
	    MaximumFinder fm = new MaximumFinder();
	    ByteProcessor maxIp = fm.findMaxima(ipfloat, 1.5, ImageProcessor.NO_THRESHOLD, MaximumFinder.SEGMENTED, false, true);
	    ips.copyBits(maxIp, 0, 0, Blitter.COPY);
	    ips.invert();
	    imps.setProcessor(null, ips);
		}
    
	    
	    //nochmal nach Formen durchchecken
	    floh = 20;//Mindestgröße für Daphnien
		rt.reset();
		pa.analyze(imps);
	    larven (rt, imps, ips, floh);//zu Kleine, Wasserflöhe, Kratzer (zu lang und dünn)und Boden weg
	    imps.setProcessor(null, ips);

	}//3 Glasfotos werden abgearbeitet
	}//Bilder 2 und 3 sind keine Dummies
		
		
}//void-run zu





int rundDmitCweg (ResultsTable rt, ImageProcessor ip, int aLim, int xwert){
	int anz = rt.getCounter();
    int anzDaph = 0;

	float[] c = rt.getColumn(ResultsTable.CIRCULARITY);
	float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
	
	int[] x = new int[anz];
	int[] y = new int[anz];
	
	for (int i=0; i<anz; i++){
		x[i]=(int)rt.getValue("XStart", i);
		y[i]=(int)rt.getValue("YStart", i);}
	
	Wand w = new Wand (ip);
	PolygonRoi roi;
	ip.setValue(255);	//IDFarbe gemäß Tabelle	

	
	for (int ii=0; ii<anz; ii++){
		if (c[ii] > 0.75 || a[ii]<aLim || x[ii]<xwert){//wenn zu rund, zu klein oder zu nah am Boden, dann löschen
		if(ip.get(x[ii], y[ii])==0){
		w.autoOutline(x[ii], y[ii], 0, 0);
		roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
		ip.setMask(roi.getMask());
		ip.setRoi(roi.getBounds()); 
		ip.fill(ip.getMask());
		ip.resetRoi();
		if(c[ii] > 0.75 && a[ii]>aLim) //nur die Daphnien werden gezählt
		anzDaph++;}}}

ip.resetRoi();	
return anzDaph;

}


//larven (rt, imps, ips, floh);//zu Kleine, Wasserflöhe, Kratzer (zu lang und dünn)und Boden weg 
void larven (ResultsTable rt, ImagePlus imp, ImageProcessor ip, int aLim){
		
		int anz = rt.getCounter();
		int anz2=0;
						
		float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
		float[] c = rt.getColumn(ResultsTable.CIRCULARITY);
		float[] sl = rt.getColumn(ResultsTable.ANGLE);// get circularity measurements
		float[] min = rt.getColumn(ResultsTable.MINOR);
		float[] maj = rt.getColumn(ResultsTable.MAJOR);
		float[] f = rt.getColumn(ResultsTable.FERET);
		float[] p = rt.getColumn(ResultsTable.PERIMETER);
				
		int[] x = new int[anz];
		int[] y = new int[anz];
		
		for (int i=0; i<anz; i++){
			x[i]=(int)rt.getValue("XStart", i);
			y[i]=(int)rt.getValue("YStart", i);}
						
		float verh;
		float peri;
		Wand wa = new Wand (ip);
		Roi roi;
		ip.setValue(100);	//IDFarbe gemäß Tabelle	
		
		for (int zz=0; zz<anz; zz++){
			if (a[zz]>10){//nur ausreichend große!! 
		    if (ip.getPixelValue(x[zz],y[zz])== 0){
		    	
		    	peri = 2*f[zz]/p[zz];		
				if (maj[zz]!=0 && min[zz]!=0)
				verh = min[zz]/maj[zz];
				else verh = 1;
			
				//falls an den Seiten und senkrecht oder unten am Boden und waagerecht: nichts
				if (((y[zz]< 80 || y[zz]>h-80 ) && (sl[zz]<5 || Math.abs(sl[zz]- 180) < 5))||(x[zz]<150  && Math.abs(sl[zz]-90)<30 )){}
				//ansonsten: sammeln, wenn wie Larve
								
				else if ((a[zz]>30 && a[zz]<650 && min[zz]>3)   //muss in jedem Fall erfüllt sein
				   &&(	     (verh < 0.32 && peri > 0.79 )//eindeutig Larve!!
						 ||  (verh < 0.25 && peri > 0.77 )//wenn verh strenger, dann peri einfacher!!
				         ||  (a[zz]>350 && a[zz]<650 && verh < 0.25 && peri > 0.74)//große larven haben deutliche Saugrohr, was peri erniedrigt
				         ||  (verh > 0.15 && verh < 0.7  && c[zz] > 0.1 && c[zz] < 0.5)//krumme Larve??
				      ))   
				
				   /**
				else if ((a[zz]>30 && a[zz]<650 && min[zz]>3) && //muss auf jeden Fall erfüllt sein!!
					((verh > 0.15 && verh < 0.35 && c[zz] > 0.1 && c[zz] < 0.65) || //Larve gestreckt
					 (verh > 0.15 && verh < 0.7  && c[zz] > 0.1 && c[zz] < 0.5)))   //oder Larve krumm
				*/   
				
				   
				{
					
					wa.autoOutline(x[zz], y[zz], 0, 0);//liegt auf ipTeile
					roi= new PolygonRoi(wa.xpoints,wa.ypoints,wa.npoints, Roi.NORMAL);
					ip.setMask(roi.getMask());
					ip.setRoi(roi.getBounds()); 
					ip.fill(ip.getMask());
					ip.resetRoi();
					anz2++;}
		}}}
		imp.setProcessor(null, ip);
		ip.resetRoi();
		if(anz2>0){
	
		ip.setThreshold(99, 101, ImageProcessor.BLACK_AND_WHITE_LUT);
		imp.setProcessor(null, ip);
		bp = (ByteProcessor)ip;
		bp.applyLut();
		ip.copyBits(bp, 0, 0, Blitter.COPY);
	    imp.setProcessor(null, ip);
		}
		
		else{
		ip.resetRoi(); 
		ip.min(255);}
		
}

}







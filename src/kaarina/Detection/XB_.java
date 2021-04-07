import ij.IJ;
import ij.ImagePlus;
import ij.WindowManager;
import ij.gui.PolygonRoi;
import ij.gui.Roi;
import ij.gui.Wand;
import ij.measure.Measurements;
import ij.measure.ResultsTable;
import ij.plugin.PlugIn;
import ij.plugin.filter.Analyzer;
import ij.plugin.filter.ParticleAnalyzer;
import ij.process.Blitter;
import ij.process.ColorProcessor;
import ij.process.ImageProcessor;




public class XB_ implements PlugIn, Measurements {

	/** Display results in the ImageJ console. */
	public static final int SHOW_RESULTS = 1, SHOW_OUTLINES = 4, MIN =12, SHOW_SIZE_DISTRIBUTION = 16, DIFFERENCE=8, COPY=0;
	public static final int SHOW_PROGRESS = 32, CLEAR_WORKSHEET = 64, RECORD_STARTS = 128,DISPLAY_SUMMARY = 256, SHOW_NONE = 512,BLACK = -16777216;
	protected static final int NOTHING=0,OUTLINES=1,MASKS=2,ELLIPSES=3;
	static final int R=0, G=1, B=2;	
	
	ImagePlus imp, imp2;
	ImageProcessor ip, ip2;
	ColorProcessor cp;
	int w,h;
	int measurements,options;
	int thr;
	int xblau;
	int aLim=20000;
	ResultsTable rt = new ResultsTable();

	
//--------------------------------------------------------------------------------------	
	public void run(String arg) {
		if (IJ.versionLessThan("1.37s"))
			return;
		
		//	Fläche messen, da Voraussetzung für Lageberechnung
		measurements = Analyzer.getMeasurements(); // defined in Set Measurements dialog
		Analyzer.setMeasurements(0);
		Analyzer.setMeasurements(Measurements.AREA+Measurements.PERIMETER+Measurements.ELLIPSE+Measurements.CIRCULARITY+Measurements.RECT+Measurements.MEAN+Measurements.MIN_MAX+Measurements.STD_DEV);
		measurements |= AREA+PERIMETER+ELLIPSE+CIRCULARITY+STD_DEV+MEAN+MIN_MAX;  //make sure area is measured
		options = CLEAR_WORKSHEET+RECORD_STARTS;//+SHOW_NONE;
		Analyzer.setMeasurements(measurements);
		ParticleAnalyzer pa = new ParticleAnalyzer(options, measurements, rt, 0, 99999999);

	
	imp  = WindowManager.getImage("0");
	ip = imp.getProcessor();
	w=imp.getWidth();
	h=imp.getHeight();
	
	ip2=ip.createProcessor(w, h);
	ip2.copyBits(ip, 0, 0, Blitter.COPY);
	ip2=ip2.convertToByte(false);
	imp2 = new ImagePlus ("Blue", ip2);
	imp2.show();
    
    
    //Detektion Band (zweimal: int rot1, int rot2, int grün1, int grün2, int blau1, int blau2)	
    //band(0,100,0,255,150,255,0,200,0,255,230,255);
    band(0,100,0,255,150,255,0,15,0,255,64,255); //Bei Renato neu gesetzt, da die Bänder sehr dunkel waren...
	rt.reset();
	pa.analyze(imp2);
	Groß (rt, imp2, ip2, aLim);//Alle Teile die größer als aLim sind, werden aufgehoben.
    Blau(imp2, ip2);//was blau und größer als 500
    
    //ich glaub es gibt später wieder Probleme mit wand.Tool
    ip2.setValue(255);
    ip2.drawLine(0, 0, w-1, 0);
    ip2.drawLine(0, h-1, w-1, h-1);
    imp2.setProcessor(null,ip2);

}

		
void band(int r1, int r2, int g1, int g2,int b1, int b2,int R1, int R2, int G1, int G2,int B1, int B2){
		cp=(ColorProcessor)ip;
		int[]RGB = new int [3];
			    
		for(int y = 0; y<cp.getHeight(); y++){
		for(int x = 0; x<cp.getWidth(); x++){
			cp.getPixel(x,y,RGB);
			if((RGB[R]>=r1 & RGB[R]<=r2)&(RGB[G]>=g1 & RGB[G]<=g2)&(RGB[B]>=b1 & RGB[B]<=b2)||
			   (RGB[R]>=R1 & RGB[R]<=R2)&(RGB[G]>=G1 & RGB[G]<=G2)&(RGB[B]>=B1 & RGB[B]<=B2))
			ip2.putPixel(x, y, 0);
			else ip2.putPixel(x, y, 255);
		}}
		
		ip2.erode();
		ip2.dilate();
		imp2.setProcessor(null, ip2);
			
}


void Groß (ResultsTable rt, ImagePlus imp, ImageProcessor ip, int aLim){
	int anz = rt.getCounter();
    if (anz == 0)
		return;
		
	float[] a = rt.getColumn(ResultsTable.AREA); // muss noch in wahre Pixellänge umgerechnet werden
	
	ip.min(10);
	ip.setValue(0);
	Wand w = new Wand (ip);
	PolygonRoi roi;

		
	for (int ii=0; ii<anz; ii++){
		if (ip.get((int)rt.getValue("XStart", ii), (int)rt.getValue("YStart", ii))<255){
			if(a[ii]>aLim){
			w.autoOutline((int)rt.getValue("XStart", ii), (int)rt.getValue("YStart", ii), 10, 10);
			roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
			ip.setMask(roi.getMask());
			ip.setRoi(roi.getBounds()); 
		    ip.fill(ip.getMask());
}}}
ip.threshold(0);
imp.setProcessor(null,ip);	
}




void Blau(ImagePlus imp, ImageProcessor ip){
	
	int xneu;
	int xalt=w;
	int yalt=h;
	
	for(int yy=30; yy<h-30; yy+=20){
		xneu=w/2;
		while (ip.get(xneu,yy)== 255 & xneu<w){//von unten nach oben: wo fängt Rand an?
			xneu = xneu+1;}
		
		if(xneu<xalt)
		{xalt=xneu;
		 yalt=yy;}
	}
	
	ip.min(10);
	ip.setValue(0);
	Wand ww = new Wand (ip);
	Roi roi;
	ww.autoOutline(xalt, yalt, 10, 10);
	roi= new PolygonRoi(ww.xpoints,ww.ypoints,ww.npoints, Roi.NORMAL);
	ip.setMask(roi.getMask());
	ip.setRoi(roi.getBounds()); 
	ip.fill(ip.getMask());
	ip.resetRoi();
	imp.setProcessor(null,ip);
	
	ip.threshold(0);
	imp.setProcessor(null,ip);

}
}



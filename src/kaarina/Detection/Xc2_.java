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
import ij.process.ImageProcessor;

public class Xc2_ implements PlugIn, Measurements {
	public static final int CLEAR_WORKSHEET = 64, RECORD_STARTS = 128;
	//static public final int RED_LUT=0, BLACK_AND_WHITE_LUT=1, NO_LUT_UPDATE=2, OVER_UNDER_LUT=3;
	
	ImagePlus imp, impTemp, impColl;
	ImageProcessor ip, ipTemp, ipColl;
	int w,h;
	int measurements,options;
	ResultsTable rt = new ResultsTable();
	int stop[]=new int [2];
	String pfad;
	
	public void run(String arg) {

	imp = WindowManager.getImage("viele");
	ip = imp.getProcessor();//original in sw speichern
	w=imp.getWidth();
	h=imp.getHeight();
	
	ipColl= ip.createProcessor(w,h);
	ipColl.invert();
	impColl = new ImagePlus ("Coll", ipColl);
	impColl.show();
		
	//hiermit wird gearbeitet
	ipTemp= ip.createProcessor(w,h);
	ipTemp.copyBits(ip, 0, 0, Blitter.COPY);
	impTemp = new ImagePlus ("temp", ipTemp);
	impTemp.show();
	
	
	//	Fläche messen, da Voraussetzung für Lageberechnung
	measurements = Analyzer.getMeasurements(); // defined in Set Measurements dialog
	Analyzer.setMeasurements(0);
	Analyzer.setMeasurements(Measurements.AREA+Measurements.PERIMETER+Measurements.ELLIPSE+Measurements.CIRCULARITY+Measurements.RECT+Measurements.MEAN+Measurements.MIN_MAX+Measurements.STD_DEV);
	measurements |= AREA+PERIMETER+ELLIPSE+CIRCULARITY+STD_DEV+MEAN+MIN_MAX;  //make sure area is measured
	options = CLEAR_WORKSHEET+RECORD_STARTS;//+SHOW_NONE;
	Analyzer.setMeasurements(measurements);
	ParticleAnalyzer pa = new ParticleAnalyzer(options, measurements, rt, 0, 99999999);

	
//----------------------------------------------------------------------------------------------
	//mit adaptiven Threshold vordergrund herausschälen

	Wand ww = new Wand (ip);
	PolygonRoi roi;
	ipTemp.setValue(255);
    ww.autoOutline(w-1, 0, 0, 0);
	roi= new PolygonRoi(ww.xpoints,ww.ypoints,ww.npoints, Roi.NORMAL);
	ipTemp.setMask(roi.getMask());
	ipTemp.setRoi(roi.getBounds()); 
    ipTemp.fill(ipTemp.getMask());
    ipTemp.resetRoi();
	impTemp.setProcessor(null, ipTemp);
	
	IJ.selectWindow("temp");
	IJ.run("Mean...", "radius=7");
	
	ipColl.copyBits(ip, 0, 0, Blitter.COPY);
	
	ipColl.copyBits(ipTemp, 0, 0, Blitter.SUBTRACT);
	impColl.setProcessor(null, ipColl);
	
	ipColl.threshold(8);
	impColl.setProcessor(null, ipColl);
	
	
	/*
	IJ.selectWindow("temp");
	IJ.run("Mean...", "radius=7");
	
	ipColl.copyBits(ip, 0, 0, Blitter.COPY);
	IJ.selectWindow("Coll");
	IJ.run("Mean...", "radius=1");//!!!!!!!den schritt gab es vorher nicht!!! Damit Rauschen der neuen Kamera entfernt...
	
	ipColl.copyBits(ipTemp, 0, 0, Blitter.SUBTRACT);
	impColl.setProcessor(null, ipColl);
	
	ipColl.threshold(6);//!!!!!!!!!!!!!!!Das war mit der alten Kamera auf 8
	impColl.setProcessor(null, ipColl);
	*/
	
	
	//den Hintrgrund als Vordergrund, Löcher vom Rand splitten und entfernen = füllen
	split (ipColl, w, h, 0);//Löcher vom Rand trennen
	impColl.setProcessor(null, ipColl);
	rt.reset();
	pa.analyze(impColl);
	kleinweg (rt, impColl, ipColl, 20);//Löcher entfernen
	ipColl.invert();
	impColl.setProcessor(null, ipColl);
		
	//----------------------------------------------------------------------------------------------
	split (ipColl, w, h, 0);// splitten, was nur noch an einem Pixel zusammenhängt
	glatt2 (ipColl, w, h);//alles glätten
	impColl.setProcessor(null,ipColl);
	
    //----------------------------------------------------------------------------------------------
	//kleine Bruchstücke löschen
	rt.reset();
	pa.analyze(impColl);
	rundDmitCweg (rt, ipColl, 40, 0);
	impColl.setProcessor(null,ipColl);
 
          
	//---------------------------------------------------------------------------------------------
	//mit Original verschneiden
    ipTemp.resetThreshold();
	ipColl.resetThreshold();
	ipColl.resetRoi();
	ipTemp.copyBits(ipColl, 0, 0, Blitter.COPY);
	impTemp.setProcessor(null,ipTemp);
	ipColl.invert();
	ipColl.copyBits(ip, 0, 0, Blitter.MIN);
	impColl.setProcessor(null,ipColl);//Biomasse in Temp
	impColl.setTitle("sez");
	
	//---------------------------------------------------------------------------------------------
	//Originalskelett erzeugen
	IJ.selectWindow("temp");
	IJ.run("Skeletonize");

	}	



	void kleinweg (ResultsTable rt, ImagePlus imp, ImageProcessor ip, int aLim){
		int anz = rt.getCounter();
		if (anz == 0)
			return;
			
		float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
		int[] x = new int[anz];
		int[] y = new int[anz];
			
		for (int i=0; i<anz; i++){
			x[i]=(int)rt.getValue("XStart", i);
			y[i]=(int)rt.getValue("YStart", i);}
		
		Wand w = new Wand (ip);
		PolygonRoi roi;
		ip.setValue(255);	//IDFarbe gemäß Tabelle	
			
		for (int ii=0; ii<a.length; ii++){
			if (a[ii]<aLim && ip.get(x[ii], y[ii])<255){
				w.autoOutline(x[ii], y[ii], 0, 254);
				roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
				ip.setMask(roi.getMask());
				ip.setRoi(roi.getBounds()); 
			    ip.fill(ip.getMask());
			    ip.resetRoi();}}
	}	

	
void rundDmitCweg (ResultsTable rt, ImageProcessor ip, int aLim, int xwert){
    	int anz = rt.getCounter();
	    float verh2,verh;
		float[] c = rt.getColumn(ResultsTable.CIRCULARITY);
		float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
		float[] min = rt.getColumn(ResultsTable.MINOR);
		float[] maj = rt.getColumn(ResultsTable.MAJOR);
		float[] peri = rt.getColumn(ResultsTable.PERIMETER);
		
		int[] x = new int[anz];
		int[] y = new int[anz];
		
		for (int i=0; i<anz; i++){
			x[i]=(int)rt.getValue("XStart", i);
			y[i]=(int)rt.getValue("YStart", i);}
		
		Wand w = new Wand (ip);
		PolygonRoi roi;
		ip.setValue(255);	//IDFarbe gemäß Tabelle	
	
		for (int ii=0; ii<anz; ii++){
			if (maj[ii]!=0 && min[ii]!=0){
			verh = min[ii]/maj[ii];
			verh2 = (peri[ii]-(2*maj[ii]))/2/maj[ii];}
			else {verh=1; verh2 = 1;}
						
			if ((verh > 0.4 && c[ii] > 0.6 && a[ii]<350) //wenn wie Daphnie oder Luftbläschen
					   || c[ii] > 0.75 //wenn so schön rund, dass es eigentlich nur Daphnie sein kann, egal wie groß
					   || a[ii] < aLim //wenn einfach zu klein
					   || x[ii] < xwert//wenn zu nah am Boden???
					   || verh  < 0.1  //wenn zu lang
					   || min[ii] < 3 //wenn zu schmal
					   //||(a[ii] < 200 && verh2 > 0.5)
					   ){ //wenn zu verkrüppelt
			if(ip.get(x[ii], y[ii])==0){
			w.autoOutline(x[ii], y[ii], 0, 0);
			roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
			ip.setMask(roi.getMask());
			ip.setRoi(roi.getBounds()); 
			ip.fill(ip.getMask());
			ip.resetRoi();
			impColl.setProcessor(null,ipColl);
			impColl.setProcessor(null,ipColl);}}}
	ip.resetRoi();	
	}



void split (ImageProcessor ip, int width, int height, int thr){
	int [][] pix = new int [width][height]; //Matrix mit der richtigen Größe geöffnet
	int [][] pix2 = new int [width][height];//Matrix mit der richtigen Größe geöffnet

//jetzt werden die Arrays aufgefüllt
for(int y=0;y<height;y++){
	for(int x=0;x<width;x++){
	pix[x][y]=ip.getPixel(x,y);//Rest
	pix2[x][y]=pix[x][y];
	}}

int[] table  =
//0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1
 {0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,1,1,0,1,1,1,0,1,0,0,0,1,0,0,
  0,1,1,1,1,1,1,1,0,1,0,0,0,1,0,0,0,1,1,1,1,1,1,1,0,1,0,0,0,1,0,0,
  0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  0,1,1,1,1,1,1,1,0,1,0,0,0,1,0,0,0,1,1,1,1,1,1,1,0,1,0,0,0,1,0,0,
  0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,
  0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,
  0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0};


double p1, p2, p3, p4, p6, p7, p8, p9;
int bgColor = 255;

int index, code;
for (int y=1; y<height-1; y++) {
for (int x=1; x<width-1; x++) {
				
		if (pix[x][y]!=bgColor) {
			p1 = pix[x-1][y-1];
			p2 = pix[x  ][y-1];
			p3 = pix[x+1][y-1];
			p4 = pix[x-1][y  ];
			p6 = pix[x+1][y  ];
			p7 = pix[x-1][y+1];
			p8 = pix[x  ][y+1];
			p9 = pix[x+1][y+1];
			index = 0;
			if (p1!=bgColor) index |= 1;
			if (p2!=bgColor) index |= 2;
			if (p3!=bgColor) index |= 4;
			if (p6!=bgColor) index |= 8;
			if (p9!=bgColor) index |= 16;
			if (p8!=bgColor) index |= 32;
			if (p7!=bgColor) index |= 64;
			if (p4!=bgColor) index |= 128;
			code = table[index];
			if (code==1) {
			pix2[x][y] = bgColor;}
		}
}}

for (int x=0; x<width; x++) {//plotten
for (int y=0; y<height; y++){
	ip.putPixel(x,y, pix2[x][y]);
	}}

}

void glatt2 (ImageProcessor ip, int width, int height){

int [][] pix = new int [width][height]; //Matrix mit der richtigen Größe geöffnet

for(int y=0;y<height;y++){
	for(int x=0;x<width;x++){
	pix[x][y]=ip.getPixel(x,y);//Rest
	}}

int[] table  =
//0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1
 {0,1,1,0,1,0,0,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,
  1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,
  1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,
  1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,
  0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,
  0,0,0,2,0,0,0,2,0,0,0,2,0,0,0,2,0,0,0,2,0,0,0,2,2,2,2,2,2,2,2,2};


double p1, p2, p3, p4, p6, p7, p8, p9;
int bgColor = 255;
int vgColor = 0;

int index, code;
for (int y=1; y<height-1; y++) {
for (int x=1; x<width-1; x++) {
		
			p1 = pix[x-1][y-1];
			p2 = pix[x  ][y-1];
			p3 = pix[x+1][y-1];
			p4 = pix[x-1][y  ];
			p6 = pix[x+1][y  ];
			p7 = pix[x-1][y+1];
			p8 = pix[x  ][y+1];
			p9 = pix[x+1][y+1];
			index = 0;
			if (p1!=bgColor) index |= 1;
			if (p2!=bgColor) index |= 2;
			if (p3!=bgColor) index |= 4;
			if (p6!=bgColor) index |= 8;
			if (p9!=bgColor) index |= 16;
			if (p8!=bgColor) index |= 32;
			if (p7!=bgColor) index |= 64;
			if (p4!=bgColor) index |= 128;
			code = table[index];
			//if(code==0 && v==0)
				//v=pass;
			if (code==1 && pix[x][y]==vgColor) {
			pix[x][y] = bgColor;}
			if (code==2 && pix[x][y]==bgColor) {
			pix[x][y] = vgColor;}
}}

for (int x=0; x<width; x++) {//plotten
for (int y=0; y<height; y++){
	ip.putPixel(x,y, pix[x][y]);
	}}

}


}






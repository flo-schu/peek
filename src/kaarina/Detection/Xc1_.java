
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


    

public class Xc1_ implements PlugIn, Measurements {

	/** Display results in the ImageJ console. */
	public static final int SHOW_RESULTS = 1, SHOW_OUTLINES = 4, MIN =12, SHOW_SIZE_DISTRIBUTION = 16, DIFFERENCE=8, COPY=0;
	public static final int SHOW_PROGRESS = 32, CLEAR_WORKSHEET = 64, RECORD_STARTS = 128,DISPLAY_SUMMARY = 256, SHOW_NONE = 512,BLACK = -16777216;
	//public static final int AREA=0, MAJOR = 15, MINOR = 16 ;
	protected static final int NOTHING=0,OUTLINES=1,MASKS=2,ELLIPSES=3;
		
 	

    int ob=0;//wo fängt der obere Suchbereich an?
    int[] xblau;
	ImagePlus imp,impRed,impGreen,impBlue,impRand;
	ImageProcessor ip,ip2,ip3,ip4,ip5,ipRed,ipGreen,ipBlue,ipRand;
	int w,h;
	int measurements,options;
	int thr;
	int stdGr = 5;//Toleranz der %Standardabweichung
	double schnitt=110;//wieviel soll an beiden Rändern abgeschnitten werden?
	int zu=100; //was vom Grenzwert noch abgezogen werden soll...
	int sprung=25;//geduldeter Pixelsprung am Rand
	String pfad;
	ResultsTable rt = new ResultsTable();
	int[] kleber=new int [2];
	int extra=10;
	int dist = 400;//Zum Aufziehen des Rechtecks
	
//--------------------------------------------------------------------------------------	
	public void run(String arg) {
			
		imp  = WindowManager.getImage("0");
		ip3 = imp.getProcessor();

		//Seitenränder abschneiden
		w=imp.getWidth();
		h=imp.getHeight();
		schnitt= 110;
		Roi roi3 = new Roi(0,(int)schnitt,w,h-2*(int)schnitt);
		ip3.setRoi(roi3);
		ip=ip3.crop();
		ip3.resetRoi();
		imp.setProcessor(null,ip);
		w=imp.getWidth();
		h=imp.getHeight();
								
		ip2 = ip.createProcessor(w, h);
		ip2.copyBits(ip, 0, 0, Blitter.COPY);
		
		ip3 = ip.createProcessor(w, h);
		ip3.copyBits(ip, 0, 0, Blitter.COPY);
		ip3=ip3.convertToByte(false);
		ip4 = ip3.createProcessor(w, h);
				
		//Flächenmessung
		measurements = Analyzer.getMeasurements(); // defined in Set Measurements dialog
		Analyzer.setMeasurements(0);
		measurements |= AREA+PERIMETER+ELLIPSE;  //make sure area is measured
		options = CLEAR_WORKSHEET+RECORD_STARTS;//+SHOW_NONE;
		Analyzer.setMeasurements(measurements);
		ParticleAnalyzer pa = new ParticleAnalyzer(options, measurements, rt, 0, 99999999);
					
//--------------------------------------------------------------------------------------			
		
		IJ.run("XB ");
		
		impBlue =  WindowManager.getImage("Blue");
		ipBlue = impBlue.getProcessor();
		ipBlue.setValue(255);
		ipBlue.drawLine(0, 0, w-1, 0);//Felher in ImageJ, ab und zu selektiert wand sonst das weiße...
		impBlue.setProcessor(null, ipBlue);
		
		pa.analyze(impBlue);//Lage des blauen Bands berechnen
		xblau = ortgOb (ipBlue, rt);
		
//--------------------------------------------------------------------------------------		
//An dieser Stelle könnte man noch eine Farbkorrektur einbauen:	*************
/*		ColorProcessor cp;
		int Red=0, Green=0, Blue=0;
		cp=(ColorProcessor)ip;
		int[]RGB = new int [3];
			    
		for(int y = 0; y<cp.getHeight(); y++){
			cp.getPixel(xblau - 20,y,RGB);
			Red=Red+RGB[0];
			Green=Green+RGB[1];
			Blue=Blue+RGB[2];}
        Red=Red/cp.getHeight();
        Green=Green/cp.getHeight();
        Blue=Blue/cp.getHeight();
*/		
//--------------------------------------------------------------------------------------		
//Automatischer Threshold in der richtigen Höhe:
		

//bunte Bilder auf Graustufe setzen
		ip=ip.convertToByte(false); 
		imp.setProcessor(null,ip);
//Rechteck um den Aufkleber aufziehen, damit automatischer Threshold für den Bereich nahe der Wasseroberfläche bestimmt wird
		Roi roiT = new Roi(xblau[1]-dist,0,dist,h);//untere Teil des Bildes
		ip.setRoi(roiT);
		ip5 = ip.createProcessor(w, h);
		ip5.copyBits(ip, 0, 0, Blitter.COPY);
		imp.setProcessor(null,ip5);
		ip5=ip.crop();
		imp.setProcessor(null,ip5);
		ip.resetRoi();

		int thr=ip5.getAutoThreshold();
		ip.threshold(thr-20);
		imp.setProcessor(null,ip);
		if(ip.getPixel(w,0)==0)
		ip.invert();
		imp.setProcessor(null,ip);		

	
//Seitenerode: Durchläufe 10
		int anzLoop = 10;
		seitensplit(ip, xblau[0], anzLoop);
		imp.setProcessor(null, ip);
	
		
//wo ist die große Fläche??	
		ip.setValue(255);	//IDFarbe gemäß Tabelle	
		ip.drawLine(w/2, 0, w/2, h);
		imp.setProcessor(null,ip);
		
		rt.reset();
		pa.analyze(imp);
		ortgGlas (ip, imp, rt, xblau[0], dist, 500);;//Kleine weg wie gehabt 

//--------------------------------------------------------------------------------------		
//blaues Band und Glas verschneiden:
		ipBlue.copyBits(ip, 0, 0, Blitter.AND);
		impBlue.setProcessor(null,ipBlue);//oder p4??
		
//in 10-Schritten die Y-Achse ablaufen und x-werte der Grenze sammeln
//gr[0]= x-Werte des hellen Glasrandes
//gr[1]= y-Werte
//gr[2]= x-Werte des blauen Bandes		
		
		int [][] p = new int [w][h]; 

		for(int y=0;y<h;y++){
			for(int x=0;x<w;x++){
			p[x][y]=ipBlue.getPixel(x,y);//die größte Randfläche
		}}
		
		int zeile = (int)Math.ceil(h/20)+1;
		int [][] gr = new int [2][zeile];
		int zei = 0;
		int xneu;
		for (int yy = 0; yy<h; yy+=20){ //von oben nach unten: die ersten X-Werte aufschreiben
			xneu=xblau[0]-dist/2;
			while (p[xneu][yy]== 255 && xneu<(xblau[0]+(dist/2))){//von unten nach oben: wo fängt Rand an?
				xneu = xneu+1;}
			gr[0][zei]=xneu;
			gr[1][zei]=yy;
			zei++;}	


		
//Glasrandreparatur: Sprünge ausgleichen und überall ein bisschen dazu
		for(int z=1; z<zeile;z++){
			//if(gr[0][z]>xblau + dist/5 || gr[0][z]<xblau - dist/3)//Sprünge??
			//{gr[0][z]=xblau;}//dann ersetzen durch xblau
		gr[0][z]=gr[0][z]-5;}//ein bisschen dazu
		
		//Glasrandreparatur
		int sprung=20;
		int zeilH = zeile/2;
		for(int z=0+zeilH; z>0;z--){//Wanderung von Mitte nach oben
			if((gr[0][z]>gr[0][z+1])||(gr[0][z]<gr[0][z+1]-sprung) )
				gr[0][z]=gr[0][z+1];}
			
		for(int z=zeile-zeilH; z<zeile;z++){//Wanderung von Mitte nach unten
			if((gr[0][z]>gr[0][z-1])||(gr[0][z]<gr[0][z-1]-sprung))
				gr[0][z]=gr[0][z-1];}		
		
//Randpunkte für den Ausschnitt überschreiben
		gr[0][0]=w-1;
		gr[1][0]=0;
		gr[1][1]=0;
		gr[0][zeile-1]=w-1;
    	gr[1][zeile-2]=h-1;
		gr[1][zeile-1]=h-1; 
		
//von punkt zu punkt ne Linie ziehen
		ip2=ip2.convertToByte(false);
		imp.setProcessor(null, ip2);
		ip2.min(1);//es gibt nichts total schwarzes im Bild
		ip2.setValue(0);
		ip2.setLineWidth(2);
		Roi roi;
		roi = new PolygonRoi(gr[0],gr[1],zeile,Roi.TRACED_ROI);		
		PolygonRoi proi = (PolygonRoi)roi;
		proi.drawPixels(ip2);
		ip2.resetRoi();
		
//oberhalb der Linie schwarz einfärben
		Wand wa = new Wand (ip2);
		wa.autoOutline(w-5, 5, 1, 255);
		roi= new PolygonRoi(wa.xpoints,wa.ypoints,wa.npoints, Roi.NORMAL);
		ip2.setMask(roi.getMask());
		ip2.setRoi(roi.getBounds()); 
	    ip2.fill(ip2.getMask());
	    ip2.resetRoi();
	    imp.setProcessor(null, ip2);
		ip2 = imp.getProcessor();
		ip3 = imp.getProcessor();
		
//obere Teil des Bildes
		Roi roi2 = new Roi(xblau[0]-200,0,300,h);//**********************
		ip2.setRoi(roi2);
		ip2=ip2.crop();
		ip2.resetRoi();
		ImagePlus imp2 = new ImagePlus ("viele", ip2);
		imp2.show();

//untere Teil des Bildes		
		roi2 = new Roi(0,0,xblau[0]-200,h);
		ip3.setRoi(roi2);
		ip3=ip3.crop();
		ip3.resetRoi();
		imp.setProcessor(null, ip3);
				
//--------------------------------------------------------------------------------------		
		
		impBlue.unlock();
		impBlue.changes = false;
		impBlue.close();
			
}		

	
void  seitensplit(ImageProcessor ip, int xblau, int anzLoop) {
		int xminus = 200;//nur x-werte von xblau - xminus...
		int xplus = 150; //...bis xblau + xplus
				
		ipRand = ip.createProcessor(w, h);
		ipRand.copyBits(ip, 0, 0, Blitter.COPY);
		ipRand.erode();
		ipRand.copyBits(ip, 0, 0, Blitter.DIFFERENCE);
		ipRand.invert();

		int i;
		for (int y=1; y<h-1; y++) {
		for (int x=xblau-xminus; x<xblau+xplus; x++) {
		if(ipRand.get(x, y)==0 && ip.get(x, y)==0){
		i=0;
		while(ip.get(x, y+i)==0 && i<anzLoop && y+i<h-1){	
		ip.putPixel(x,y+i, 255);	
		i++;}
		i=0;
		while(ip.get(x, y-i)==0 && i<anzLoop && y-i>0){	
		ip.putPixel(x,y-i, 255);	
		i++;}
 }}}
}		


int[] ortgOb(ImageProcessor ip, ResultsTable rt){
	int[]xwert = {w,0};
	int anz = rt.getCounter();
	
	float[] a = rt.getColumn(ResultsTable.AREA); 
	int[] x = new int[anz];
	int[] y = new int[anz];
			
	for (int i=0; i<anz; i++){
		x[i]=(int)rt.getValue("XStart", i);
		y[i]=(int)rt.getValue("YStart", i);	}

	float areaAlt = 0;
	int xalt=0;
	int yalt=0;
			
	for (int ii=0; ii<anz; ii++){//Wo ist die größte Fläche??
	if (a[ii]>areaAlt){
		areaAlt = a[ii];
		xalt = x[ii];
		yalt = y[ii];}}
	
	Wand wand = new Wand (ip);//Wo liegen die x und y-Punkte
	wand.autoOutline (xalt,yalt);	
	int[] xx = wand.xpoints;
	int wAnz = wand.npoints;
		
		for (int jj=0; jj< wAnz; jj++){
			if( xx[jj]< xwert[0] & xx[jj]>w/3)
				xwert[0] = xx[jj];
			if( xx[jj]> xwert[1] & xx[jj]>w/3)
				xwert[1] = xx[jj];}
		
return xwert;}


void ortgGlas(ImageProcessor ip, ImagePlus imp, ResultsTable rt, int xblau, int dist, int aLim){
		int anz = rt.getCounter();
			
		
		float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
		float[] sl= rt.getColumn(ResultsTable.ANGLE); 
		float[] min = rt.getColumn(ResultsTable.MINOR);
		float[] maj = rt.getColumn(ResultsTable.MAJOR);
		int[] x = new int[anz];
		int[] y = new int[anz];
		for (int i=0; i<anz; i++){
			x[i]=(int)rt.getValue("XStart", i);
			y[i]=(int)rt.getValue("YStart", i);}
		float verh;
		float areaAlt=0;
		int xalt=0, yalt=0;
		
		ip.min(10);
		ip.setValue(0);
		Wand ww = new Wand (ip);
		Roi roi;
		
		
		
		for (int ii=0; ii<anz; ii++){
			if (a[ii]>=aLim && x[ii]>xblau-200 && x[ii]<xblau+500 && ip.getPixelValue(x[ii],y[ii])== 10){//wenn größer als 500 Pixel und oben
				if (a[ii]>areaAlt){
				areaAlt = a[ii];
				xalt = x[ii];
				yalt = y[ii];}
				
			    verh = min[ii]/maj[ii];
			
				if (verh < 0.05 && sl[ii]>80 && sl[ii]<100){//sammeln, wenn lang und dünn parallel zum Glasrand 
					ww.autoOutline(xalt, yalt, 10, 10);
					roi= new PolygonRoi(ww.xpoints,ww.ypoints,ww.npoints, Roi.NORMAL);
					ip.setMask(roi.getMask());
					ip.setRoi(roi.getBounds()); 
					ip.fill(ip.getMask());
					ip.resetRoi();
					imp.setProcessor(null,ip);}
			}
		}
		
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
		






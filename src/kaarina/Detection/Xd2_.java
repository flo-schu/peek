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
import ij.process.BinaryProcessor;
import ij.process.Blitter;
import ij.process.ByteProcessor;
import ij.process.ImageProcessor;



//zwischendurch mal kontrollieren bzw. ersetzen: alles identisch mit daph2allein außer Zeile xxxxx
public class Xd2_ implements PlugIn, Measurements {

	/** Display results in the ImageJ console. */
	public static final int SHOW_RESULTS = 1, SHOW_OUTLINES = 4, MIN =12, SHOW_SIZE_DISTRIBUTION = 16, DIFFERENCE=8, COPY=0;
	public static final int SHOW_PROGRESS = 32, CLEAR_WORKSHEET = 64, RECORD_STARTS = 128,DISPLAY_SUMMARY = 256, SHOW_NONE = 512,BLACK = -16777216;
	//public static final int AREA=0, MAJOR = 15, MINOR = 16 ;
	protected static final int NOTHING=0,OUTLINES=1,MASKS=2,ELLIPSES=3;
		
	
	int aLim=10;//wird verwendet in den Funktionen: rundDmitC, kleben und kleinweg, wird hier allerdings neu gesetzt,
	//rundDmitC(floh=20); kleben (floh=30); kleinweg (grenz=5)
	int[] kleber=new int [2];
	int boden =280;
	
	ImageProcessor ips,ips_,ips_1,ips_2, ips_3, ipzw;
	BinaryProcessor bps;
	ImagePlus imps;
	int w,h;
	int measurements,options;
	int thr;
	int bord=0;
	
	
	ResultsTable rt = new ResultsTable();
	
//--------------------------------------------------------------------------------------	
	public void run(String arg) {
	
	//Fläche messen, da Voraussetzung für Lageberechnung
	measurements = Analyzer.getMeasurements(); // defined in Set Measurements dialog
	Analyzer.setMeasurements(0);
	measurements |= AREA+PERIMETER+ELLIPSE+CIRCULARITY+MEAN+FERET;  //make sure area is measured
	options = CLEAR_WORKSHEET+RECORD_STARTS;//+SHOW_NONE;
	Analyzer.setMeasurements(measurements);
	ParticleAnalyzer pa = new ParticleAnalyzer(options, measurements, rt, 0, 99999999);


	String[] names1 = {"0","1", "2"};
	
		

//-------------------------------------------------------------------------------------------------				
//Fotos per Schleife hintereinander abarbeiten
		
for (int s=0;s<3;s++){
	imps  = WindowManager.getImage(names1[s]);
	ips = imps.getProcessor();
	w = ips.getWidth(); //x-werte
	h = ips.getHeight(); //y-werte
	System.out.println("hello");	// test flo

	
	//bunte Bilder auf Graustufe setzen
	ips=ips.convertToByte(false); 
	imps.setProcessor(null,ips);	
	ips_=ips.createProcessor(w, h);
	ips_1=ips.createProcessor(w, h);
	ips_2=ips.createProcessor(w, h);
	ips_3=ips.createProcessor(w, h);
	ips_.copyBits(ips, 0, 0, Blitter.COPY);
	ips_=ips_.convertToByte(false); 
	ips_1=ips_1.convertToByte(false); 
	ips_2=ips_2.convertToByte(false); 
	ips_3=ips_3.convertToByte(false); 
	imps.setProcessor(null,ips_);
	
	
	//wo alte Schnittlinie
	if(bord==0){
	bord=w-1;
	while (ips_.get(bord, 0)==0 & ips_.get(bord, h-1)==0 & bord>h/2){bord--;}
	}
	
	
	//zu kleine Objekte und Mückenlarven entfernen
	thr=45;//war in alter Version auf 45, hatte ich mit neuer Kamera auf 70 gestellt, aber jetzt wieder zurück....
	ips_.threshold(thr);//Original als binär
	ips_.invert();
	imps.setProcessor(null,ips_);	
	
	
	//splitten und glätten
	//imps.setProcessor(null,ips_);
	ips_.erode();
	ips_.dilate();
	imps.setProcessor(null,ips_);
	
	
	//alle Objekte die Rand schneiden entfernen, da Larve oder Dreck...
	border(ips_, w, h, bord);
	imps.setProcessor(null,ips_);
	
	
	//nur Daphnien aufheben (Larven und Fehler weg)
	// Flo änderung von 20 auf 10, um neos zu detektieren.
	// Natürlich sollte beachtet werden, dass die Neos nur zu einem kleinen Zeitpunkt so 
	// klein sind. Allerdings trifft dies auf jeden Zeitschritt zu. Es würde so systematisch 
	// permanent die kleineste Größenklasse ausgeschlossen werden.
	// Wie hoch die Gefahr ist, zusätzliche Artefakte zu analysieren kann derzeit noch nicht 
	// eingeschätzt werden.
	int floh = 10;//Mindestgröße für Daphnien
	rt.reset();
	pa.analyze(imps);
	//xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	rundDmitC (rt,ips_,floh,boden);//zusätzlich: Larven weg!!
	//xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	imps.setProcessor(null,ips_);
	
	
	//komische zum bearbeiten aussortieren
	ips_1.min(255);
	rt.reset();
	pa.analyze(imps);
	extra (rt,ips_,ips_1,boden);
	//imps.setProcessor(null,ips_);//Objekte, die super sind
	//imps.setProcessor(null,ips_1);//Objekte zur Extrabehandlung
	ips_2.copyBits(ips_1, 0, 0, Blitter.COPY);
	ips_2.invert();
	ips_2.copyBits(ips, 0, 0, Blitter.MIN);
	imps.setProcessor(null,ips_2);
		
	//Objekttrennung
	//Graustufen smoothen
	for (int i=1;i<=7;i++){
	ips_2.smooth();}
	imps.setProcessor(null,ips_2);
	
	
	//dunkle Stellen auf schwarz setzen
	ips_3.min(255);
	trennung (ips_2, ips_3,w,h,thr);
	imps.setProcessor(null,ips_3);//Trennungsritzen
	//dunkle Stellen verfeinern
	bps = new BinaryProcessor((ByteProcessor)ips_3);
	bps.skeletonize();
	ips_3.copyBits(bps, 0, 0, Blitter.COPY);
	imps.setProcessor(null,ips_3);
	//kleinen Stückchen löschen
	int grenz = 5;
	rt.reset();
	pa.analyze(imps);
	kleinweg (rt, ips_3, grenz);
	imps.setProcessor(null,ips_3);//Trennungsritzen fertig
	ips_3.invert();
	
	ips_2.copyBits(ips_1, 0, 0, Blitter.COPY);
	ips_2.copyBits(ips_3, 0, 0, Blitter.MAX);
	imps.setProcessor(null,ips_1);	
	imps.setProcessor(null,ips_2);	
	//imps.setProcessor(null,ips_3);		
	
	//jetzt Watershedding
	IJ.selectWindow(names1[s]);
	IJ.run("Watershed"); 
	
		
	 //Löcher und ritzen füllen
    ips_3.copyBits(ips_2, 0, 0, Blitter.COPY);
    ips_3.dilate();
    ips_2.invert();
    
    ips_3.copyBits(ips_2, 0, 0, Blitter.MAX);
    ips_2.invert();
	//imps.setProcessor(null,ips_1);	
	//imps.setProcessor(null,ips_2);	
	//imps.setProcessor(null,ips_3);	
    glatt (ips_2, ips_3, w, h);
    imps.setProcessor(null, ips_2);
    
	
  //kleine Bruchstücke wieder rankleben
	floh=30;
    ips_3.min(255);
	rt.reset();
	pa.analyze(imps);
	kleben (rt, ips_1, ips_2, ips_3, floh, w,h);
	imps.setProcessor(null, ips_2);

	
	//-----------------------------------------------------------------------
	//nochmal: nur Daphnien aufheben (Larven und Fehler weg), Schritt fehlt bei DaphAlone
	floh = 20;//Mindestgröße für Daphnien
	rt.reset();
	pa.analyze(imps);
	//xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	rundDmitC (rt,ips_2,floh,boden);//zusätzlich: Larven weg!!
	//xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	imps.setProcessor(null,ips_2);
	//-----------------------------------------------------------------------
	
	
	//behandelte Extrastücke wieder ins Original übertragen
	ips_.copyBits(ips_2, 0, 0, Blitter.MIN);
	imps.setProcessor(null, ips_);
			


}}	
//-----------------------------------------------------------------------------------------


	void border (ImageProcessor ip, int weight, int height, int border){
		Wand w = new Wand (ip);
		PolygonRoi roi;
		ip.setValue(255);	//IDFarbe gemäß Tabelle	
		
		int[]xline={border-1,0,weight-1};
		for (int xx = 0; xx<xline.length; xx++){
		for (int yy=0; yy<height-1; yy++){
				
			if( ip.get(xline[xx], yy)==0){
			w.autoOutline(xline[xx], yy, 0, 0);
			roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
			ip.setMask(roi.getMask());
			ip.setRoi(roi.getBounds()); 
			ip.fill(ip.getMask());
			ip.resetRoi();}}}
		
		int[]yline={0,height-1};
		for (int yy = 0; yy<yline.length; yy++){
		for (int xx = 0; xx<weight-1; xx++){
		
			if( ip.get(xx, yline[yy])==0){
			w.autoOutline(xx, yline[yy], 0, 0);
			roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
			ip.setMask(roi.getMask());
			ip.setRoi(roi.getBounds()); 
			ip.fill(ip.getMask());
			ip.resetRoi();}}}
	}




	void rundDmitC (ResultsTable rt, ImageProcessor ip, int aLim, int xwert){
		int anz = rt.getCounter();
		if (anz == 0)
			return;
		float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
		float[] min = rt.getColumn(ResultsTable.MINOR);
		float[] max = rt.getColumn(ResultsTable.MAJOR);
		float[] c = rt.getColumn(ResultsTable.CIRCULARITY);
		float[] f = rt.getColumn(ResultsTable.FERET);
		float[] p = rt.getColumn(ResultsTable.PERIMETER);
		
		int[] x = new int[anz];
		int[] y = new int[anz];
		
		for (int i=0; i<anz; i++){
			x[i]=(int)rt.getValue("XStart", i);
			y[i]=(int)rt.getValue("YStart", i);}
		
		Wand w = new Wand (ip);
		PolygonRoi roi;
		ip.setValue(255);	//IDFarbe gemäß Tabelle	
		
		float verh;
		float peri;
		for (int ii=0; ii<anz; ii++){
			peri = 2*f[ii]/p[ii];
			if (max[ii]!=0 && min[ii]!=0)
				verh = min[ii]/max[ii];
			else verh = 1;
			
			/**alte Larvenerkennung
			if ((x[ii]< xwert && (verh < 0.25 || a[ii] > 600 || a[ii] <30 || c[ii] < 0.5)) //wenn am Boden...
			    
			|| ((a[ii]>30 && a[ii]<650 && min[ii]>3) && //muss auf jeden Fall erfüllt sein!!
			   ((verh > 0.15 && verh < 0.35 && c[ii] > 0.1 && c[ii] < 0.65) || //Larve gestreckt
				(verh > 0.15 && verh < 0.7  && c[ii] > 0.1 && c[ii] < 0.5)))   //oder Larve krumm
									
			|| a[ii] < aLim){
			*/	
			
			if ((x[ii]< xwert && (verh < 0.25 || a[ii] < 100 || a[ii] > 600 || c[ii] < 0.75)) //wenn am Boden, dann muss groß und perfekt sein...
				    
					|| ((a[ii]>30 && a[ii]<650 && min[ii]>3) && ( verh < 0.32 && peri > 0.79 )) //muss auf jeden Fall erfüllt sein!!
					|| ((a[ii]>30 && a[ii]<650 && min[ii]>3) && ( verh < 0.25 && peri > 0.77 )) //wenn Verhältnis streng, dann peri locker
					|| (a[ii]>350 && a[ii]<650 && verh < 0.25 && peri > 0.74)//große larven haben deutliche Saugrohr, was peri erniedrigt
					|| a[ii] < aLim){
			
			if(ip.get(x[ii], y[ii])==0){
			w.autoOutline(x[ii], y[ii], 0, 0);
			roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
			ip.setMask(roi.getMask());
			ip.setRoi(roi.getBounds()); 
			ip.fill(ip.getMask());
			ip.resetRoi();
			//imps.setProcessor(null,ip);
			}}}

	ip.resetRoi();	

	}	
	
		
	
	void extra (ResultsTable rt, ImageProcessor ip, ImageProcessor ip1, int xwert){
		int anz = rt.getCounter();
		if (anz == 0)
			return;
		float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
		float[] c = rt.getColumn(ResultsTable.CIRCULARITY);
		float[] f = rt.getColumn(ResultsTable.FERET);
		float[] p = rt.getColumn(ResultsTable.PERIMETER);
		
		int[] x = new int[anz];
		int[] y = new int[anz];
		
		for (int i=0; i<anz; i++){
			x[i]=(int)rt.getValue("XStart", i);
			y[i]=(int)rt.getValue("YStart", i);}
		
		Wand w = new Wand (ip);
		PolygonRoi roi;
		ip.setValue(255);	//IDFarbe gemäß Tabelle	
		ip1.setValue(0);
		
		float peri;
		for (int ii=0; ii<anz; ii++){
			peri = 2*f[ii]/p[ii];
							
			if (a[ii]< 650 && c[ii]>0.62 && peri > 0.72) {} //dann wohl schöne Daphnie
			else{//nochmal checken
			if(ip.get(x[ii], y[ii])==0){
			w.autoOutline(x[ii], y[ii], 0, 0);
			roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
			ip.setMask(roi.getMask());
			ip.setRoi(roi.getBounds()); 
			ip.fill(ip.getMask());
			ip.resetRoi();
			ip1.setMask(roi.getMask());
			ip1.setRoi(roi.getBounds()); 
			ip1.fill(ip1.getMask());
			ip1.resetRoi();}}}

	ip.resetRoi();	
	ip1.resetRoi();	

	}




	void kleben (ResultsTable rt, ImageProcessor ip1, ImageProcessor ip2, ImageProcessor ip3, int aLim, int width, int height){
		//ip1 = vor watershedding
		//ip2 = nach watershedding, schwarz auf weiß, durchgemessen
		//ip3 = zur Benutzung
		int anz = rt.getCounter();
		if (anz == 0)
			return;
		float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
		int[] x = new int[anz];
		int[] y = new int[anz];
		
		for (int i=0; i<anz; i++){
			x[i]=(int)rt.getValue("XStart", i);
			y[i]=(int)rt.getValue("YStart", i);}
		
		Wand w = new Wand (ip2);
		PolygonRoi roi;
		ip3.setValue(0);	//IDFarbe gemäß Tabelle	
		
		for (int ii=0; ii<anz; ii++){

			if (a[ii] < aLim){
			if(ip2.get(x[ii], y[ii])==0){
			w.autoOutline(x[ii], y[ii], 0, 0);
			roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
			ip3.setMask(roi.getMask());
			ip3.setRoi(roi.getBounds()); 
			ip3.fill(ip3.getMask());
			ip3.resetRoi();}}}


	ip3.dilate();
	imps.setProcessor(null, ip3);

	for(int yi=0;yi<height;yi++){
	for(int xi=0;xi<width;xi++){
	if(ip3.get(xi, yi)==0 && ip1.get(xi, yi)==0)
	ip2.putPixel(xi, yi, 0);
	}}//Rest

	imps.setProcessor(null, ip2);

	}
	
	
	
	
void trennung (ImageProcessor ip, ImageProcessor ip_, int width, int height, int thr){

	int x, y;
	int [][] pixel = new int [width][height]; //Matrix mit der richtigen Größe geöffnet
	
	//jetzt werden die Arrays aufgefüllt
	for(y=0;y<height;y++){
	for(x=0;x<width;x++){
	pixel[x][y]=ip.getPixel(x,y);//original
	}}
	
	//jetzt Grenzen ausfindig machen und schwarz
	for (x=1; x<width-1; x++) {
		for (y=1; y<height-1; y++) {
			// Bedingung das Umgebung heller ist:
			if(pixel[x][y]> thr){
			    if (  (pixel[x-1][y-1]> pixel[x][y] && pixel[x+1][y+1] > pixel[x][y]) 
				|| (pixel[x+1][y-1]> pixel[x][y] && pixel[x-1][y+1] > pixel[x][y])  
				|| (pixel[x+1][y  ]> pixel[x][y] && pixel[x-1][y  ] > pixel[x][y]) 
				|| (pixel[x  ][y+1]> pixel[x][y] && pixel[x  ][y-1] > pixel[x][y]) )
					{
			    	ip_.putPixel(x,y, 0);//dann wird Mittelpunkt weiss eingefärbt
					}
			 }		
			}}

}



void kleinweg (ResultsTable rt, ImageProcessor ip, int aLim){

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

	for (int ii=0; ii<anz; ii++){
		if (a[ii] < aLim){
		if(ip.get(x[ii], y[ii])==0){
		w.autoOutline(x[ii], y[ii], 0, 0);
		roi= new PolygonRoi(w.xpoints,w.ypoints,w.npoints, Roi.NORMAL);
		ip.setMask(roi.getMask());
		ip.setRoi(roi.getBounds()); 
		ip.fill(ip.getMask());
		ip.resetRoi();}}}


}




void glatt (ImageProcessor ip, ImageProcessor ip2, int width, int height){

int [][] pix = new int [width][height]; 
for(int y=0;y<height;y++){
	for(int x=0;x<width;x++){
	pix[x][y]=ip.getPixel(x,y);}}
	

int[] table  =
//0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1
 {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,
  0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,
  0,0,0,1,0,0,1,1,0,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,
  0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,
  0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1};


double p1, p2, p3, p4, p6, p7, p8, p9;
int bgColor = 255;
int vgColor = 0;
int index, code;

for (int y=1; y<height-1; y++) {
for (int x=1; x<width-1; x++) {
if(pix[x][y]==bgColor && ip2.get(x, y)==0){
		
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
			pix[x][y] = vgColor;}
			
}}}



for (int y=height-2; y>1; y--) {
for (int x=width-2; x>1; x--) {
if(pix[x][y]==bgColor && ip2.get(x, y)==0){


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
				pix[x][y] = vgColor;}
				
	}}}

for (int x=0; x<width; x++) {//plotten
for (int y=0; y<height; y++){
	ip.putPixel(x,y, pix[x][y]);
	}}
}

	
		
}


		
		





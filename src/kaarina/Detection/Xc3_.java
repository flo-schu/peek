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
import ij.plugin.filter.EDM;
import ij.plugin.filter.ParticleAnalyzer;
import ij.process.Blitter;
import ij.process.ImageProcessor;



public class Xc3_ implements PlugIn, Measurements {

	/** Display results in the ImageJ console. */
	public static final int SHOW_RESULTS = 1, SHOW_OUTLINES = 4, MIN =12, SHOW_SIZE_DISTRIBUTION = 16, DIFFERENCE=8, COPY=0;
	public static final int SHOW_PROGRESS = 32, CLEAR_WORKSHEET = 64, RECORD_STARTS = 128,DISPLAY_SUMMARY = 256, SHOW_NONE = 512;
	public static final int MAJOR = 15, MINOR = 16, BLACK = -16777216, GET_BOUNDS = 375;
	protected static final int NOTHING=0,OUTLINES=1,MASKS=2,ELLIPSES=3;
		
	
	ResultsTable rt = new ResultsTable();
	ImagePlus impOrig,impSez,impTemp,impTeile,impColl,impSize;
	ImageProcessor ipOrig,ipSez,ipTemp,ipTemp2,ipTeile,ipColl,ipSize;
    String pfad;
    int rand = 75;//weißer Rand ums Bild herum
    int w,h;
	int [][] p,p2,id,pHell,pBack; 
	float[][]pEDM;
	double [][] endpunkte;
	double[][]kurve;
	double weiss = 65535;
	
	public void run(String arg) {
	pfad="C:\\Dokumente und Einstellungen\\foit\\Eigene Dateien\\4_Versuche\\12_Nanokosmen Technik\\0_Mückendetektion\\#nichts";

	
//	------------------------------------------------------------------------------------------
//	Vorarbeiten
//	------------------------------------------------------------------------------------------		
			
	int measurements = Analyzer.getMeasurements(); // defined in Set Measurements dialog
	Analyzer.setMeasurements(0);
	Analyzer.setMeasurements(Measurements.AREA+Measurements.CIRCULARITY+Measurements.RECT+Measurements.MEAN+Measurements.MIN_MAX+Measurements.STD_DEV);
	int options=0;
	options = CLEAR_WORKSHEET+RECORD_STARTS;//+SHOW_NONE;
	Analyzer.setMeasurements(measurements);
	ParticleAnalyzer pa = new ParticleAnalyzer(options, measurements, rt, 0, 99999999);
		
	impOrig  = WindowManager.getImage("viele");
	impOrig.setTitle("viele.png");
	ipOrig = impOrig.getProcessor();
	w = ipOrig.getWidth(); //x-werte
	h = ipOrig.getHeight(); //y-werte
	IJ.selectWindow("viele.png");
	//IJ.run("Canvas Size...", "width=260 height=1316 position=Center zero");
	IJ.run("Canvas Size...", "width="+(w+2*rand)+" height="+(h+2*rand)+" position=Center zero");
	ipOrig = impOrig.getProcessor();
	
	IJ.selectWindow("sez");
	IJ.run("Canvas Size...", "width="+(w+2*rand)+" height="+(h+2*rand)+" position=Center zero");
	impSez  = WindowManager.getImage("sez");
	impSez.setTitle("sez.png");
	ipSez = impSez.getProcessor();
		
	IJ.selectWindow("temp");
	IJ.run("Canvas Size...", "width="+(w+2*rand)+" height="+(h+2*rand)+" position=Center");
	impTemp  = WindowManager.getImage("temp");
	impTemp.setTitle("skelett.png");
	ipTemp = impTemp.getProcessor();
	w = ipTemp.getWidth(); //neue x-werte
	h = ipTemp.getHeight(); //neue y-werte
  
	ipColl  = ipTemp.createProcessor(w,h);
	int x, y;
	p = new int [w][h]; 
	

//------------------------------------------------------------------------------------------

	//Schnittpunkte von Skelettlinien ausfindig machen und löschen

	for(y=0;y<h;y++){	
	for(x=0;x<w;x++){
	p[x][y]=ipTemp.getPixel(x,y);}}//das Sklelett in p-Matrix	
		
	for(int anz = 9; anz>=4;anz--){ //sukzessive wird von groß zu kleinem Knotenpunkt abgearbeitet
	for (x=1; x<w-1; x++) {
	for (y=1; y<h-1; y++) {
				
		// Bedingung das aus der Umgebung mehrere skelettlinen zulaufen:
		int count =0;
		if(p[x][y]== 0){
				for (int q = -1; q<=1;q++){
				for(int r = -1; r<=1; r++){
					if (p[x+r][y+q]==0)
						count++;}}}//Zählung: wieviele Linien laufen zu?
					if (count==anz){//wenn Knotenpunkt:
						for (int q = -1; q<=1;q++){
						for(int r = -1; r<=1; r++){
						p[x+r][y+q]=255;}}}//Knotenpunkt wird weiß gesetzt in pixel
	}}}	

//Kapier nicht warum, aber notwendig
for (x=0; x<w; x++) {
for (y=0; y<h; y++){
ipColl.putPixel(x,y, p[x][y]);}}
impColl = new ImagePlus ("Coll", ipColl);//Teilstückchen der Skelette in Coll
impColl.show();
IJ.selectWindow("Coll");
IJ.run("Skeletonize");//????????????????????????????????????????????????????????????

//plotten
IJ.newImage("Teile", "16-bit White", w, h, 1);
IJ.run("Invert LUT");
impTeile  = WindowManager.getImage("Teile");
ipTeile=impTeile.getProcessor();
ipTeile.min(weiss);
impTeile.setProcessor(null, ipTeile);

for (x=0; x<w; x++) {
for (y=0; y<h; y++){
if(ipColl.getPixel(x, y)==0){
ipTeile.putPixelValue(x,y, 0);}}}
impTeile.setProcessor(null, ipTeile);//Teilstückchen der Skelette in Teile
impColl.setProcessor(null, ipColl);//Teilstückchen der Skelette in Coll
	

//------------------------------------------------------------------------------------------
//Kurven durchschneiden

//Mit Funktion im Bild Teile die Objekte einfärben und Endpunkte in Tabelle eintragen
double [][] curve = FarbID ();
//Spalte 0 = xwert Endpunkt1
//Spalte 1 = ywert Endpunkt1
//Spalte 2 = xwert Endpunkt2
//Spalte 3 = ywert Endpunkt2
//Spalte 4 = Hypothenuse des ObjektKnickpunkts
//Spalte 5 = x-wert des Knickpunkts
//Spalte 6 = y-wert des Knickpunkts

for(y=0;y<h;y++){	
for(x=0;x<w;x++){
p[x][y]=ipTeile.getPixel(x,y);}}//Teilstückchen mit FarbID der Skelette in p (von 0 bis 65535) 

//Knickpunkt herausfinden
int x1,x2,y1,y2;
double a,b,c,alpha,hh;
for(y=1;y<h-1;y++){//laufe die Matrix ab
for(x=1;x<w-1;x++){
if(p[x][y]<weiss){//Objekt
	x1=(int)curve[0][p[x][y]];
	y1=(int)curve[1][p[x][y]];
	x2=(int)curve[2][p[x][y]];
	y2=(int)curve[3][p[x][y]];
	a=Math.pow((Math.pow(x2-x,2)+Math.pow(y2-y,2)), 0.5);
	b=Math.pow((Math.pow(x1-x,2)+Math.pow(y1-y,2)), 0.5);	
	c=Math.pow((Math.pow(x1-x2,2)+Math.pow(y1-y2,2)), 0.5);//Länge Basis
	alpha=Math.acos((Math.pow(a,2)-Math.pow(b,2)-Math.pow(c,2))/(-2*b*c));
	hh=Math.sin(alpha)*b;	
	if (hh>curve[4][p[x][y]]){
	curve[4][p[x][y]]=hh;
	curve[5][p[x][y]]=a;
	curve[6][p[x][y]]=b;
	curve[7][p[x][y]]=180/Math.PI*Math.acos(hh/a);//Winkel1
	curve[8][p[x][y]]=180/Math.PI*Math.acos(hh/b);//Winkel2
	curve[9][p[x][y]]=curve[7][p[x][y]]+curve[8][p[x][y]];//WinkelGes
	curve[10][p[x][y]]=Math.min(curve[7][p[x][y]],curve[8][p[x][y]])/curve[9][p[x][y]];//WinkelVerh
	curve[11][p[x][y]]=x;
	curve[12][p[x][y]]=y;
}}}}


//wenn Gesamtwinkel<110 Grad oder Winkelverhältnis <0.4, dann Knickpunkt löschen.
for(int i=1;i<curve[0].length;i++){
if(curve[4][i]>1 && (Math.min(curve[7][i],curve[8][i])*2 <=115 || curve[10][i]<0.4))
ipColl.putPixel((int)curve[11][i],(int)curve[12][i],255);}
impColl.setProcessor(null, ipColl);//Teilstückchen ohne Knickpunkte
ipTeile.resetRoi(); 
ipTeile.min(weiss);
impTeile.setProcessor(null, ipTeile);//leer



//------------------------------------------------------------------------------------------
//alles, was <= 2 Pixel groß ist, ist unwichtig und soll weg.
int grenz = 2;
rt.reset();
pa.analyze(impColl);
kleiner (rt, impColl, ipColl, grenz);
impColl.setProcessor(null,ipColl);//gesäuberte Teilstückchen der Skelette in Coll


//--------------------------------------------------------------------------------------------
// Helligkeit der Pixel speichern
pHell = new int [w][h];
int av,n;
for(y=0;y<h;y++){	
for(x=0;x<w;x++){
	if(ipColl.getPixel(x,y)<255){
	av=0;
	n=0;
	for(int yy=-1;yy<=1;yy++){
	for(int xx=-1;xx<=1;xx++){
	if(ipSez.getPixel(x+xx,y+yy)>0)	{
	av+=ipSez.getPixel(x+xx,y+yy);	
	n++;
	}}}
pHell[x][y]=av/n;}}}


//Helligkeit des Background berechnen u speichern
pBack = new int [w][h];
double[] greyAv = new double [w];//für Mittelwert
for (x=0;x<w;x++){
    n=0;
    for (y=0;y<h;y++){
    	if(ipOrig.get(x, y)>0){
    	greyAv[x]+=ipOrig.get(x, y);
    	n++;}}
    if(n>0){
    greyAv[x]=greyAv[x]/n;}}
for(y=0;y<h;y++){	
for(x=0;x<w;x++){
if(ipColl.getPixel(x,y)<255){
pBack[x][y]=(int)greyAv[x];}}}	


// EDM-Werte der Pixel speichern
ipSez.threshold(0);
impSez.setProcessor(null,ipSez);

EDM edm = new EDM();
impSez.setProcessor(null, ipSez);
ImageProcessor ipfloat=edm.makeFloatEDM(ipSez, 0, false);
impSez.setProcessor(null, ipfloat);

pEDM = new float [w][h];
for(y=0;y<h;y++){	
for(x=0;x<w;x++){
	if(ipColl.getPixel(x,y)<255){
	pEDM[x][y]=ipfloat.getf(x, y);}}}//das Sklelett in p-Matrix


ipSez.copyBits(ipOrig, 0, 0, Blitter.MIN);
impSez.setProcessor(null,ipSez);


//------------------------------------------------------------------------------------------
//Vorarbeiten zum Verbinden der Objektestücke

for (x=0; x<w; x++) {
for (y=0; y<h; y++){
if(ipColl.getPixel(x, y)==0)
ipTeile.putPixelValue(x,y, 0);}}


impTeile.setProcessor(null, ipTeile);//gesäuberte Teilstückchen in Teile
ipColl.min(255);
impColl.setProcessor(null, ipColl);//Coll ist leer

//Mit Funktion im Bild Teile die Objekte einfärben und Endpunkte in Tabelle eintragen
double [][] teile = FarbID ();
//Spalte 0 = xwert Endpunkt1
//Spalte 1 = ywert Endpunkt1
//Spalte 2 = xwert Endpunkt2
//Spalte 3 = ywert Endpunkt2
//Spalte 4 = Steigung Endpunkt 1
//Spalte 5 = Steigung Endpunkt 2
//Spalte 6 = ich bin ErgStück: in welcher Farbe ist einzufärben / mit welchem Objekt zu verbinden?
//Spalte 7 = ErgStück: welcher Endpunkt zur Verbindung?
//Spalte 8 = AndockStück: welcher Endpunkt zur Verbindung?
//Spalte 9 = Steigungsende x Endpunkt 1
//Spalte 10 = Steigungsende y Endpunkt 1
//Spalte 11 = Steigungsende x Endpunkt 2
//Spalte 12 = Steigungsende y Endpunkt 2

//Endpunkte schwarz in Coll plotten
int farbe = teile[0].length;
for(int i = 1; i<farbe;i++){
ipColl.putPixel((int)teile[0][i],(int)teile[1][i], 0);
ipColl.putPixel((int)teile[2][i],(int)teile[3][i], 0);}


//Endpunkte zurückverfolgen: Steigungsende und Steigung ermitteln
teile = steigung(teile,p);



//------------------------------------------------------------------------------------------
//Objekte verbinden:
//jetzt alle Punkt durchgehen: wenn in Umgebung von 10 Pixeln zu Quadrat ein anderer Punkt
//vorhanden ist, der die gleiche Steigung hat und die Verbindung zwischen den beiden Punkten
//ebenfalls eine ähnliche Steigung hat und es nicht zu dunkel ist zwischen den Punkten, 
//dann Punkte verbinden auf Coll plotten

teile = verbinden(teile, ipTeile, ipColl);

//Jetzt gemäß den Tabelleninformationen alles einfärben
//1.Neues Teilstück
Wand wa = new Wand (ipTeile);
Roi roi;
int ep1,ep2,ep2neu,iineu;
//1.Einzelteile
for(int ii = 1; ii<teile[0].length;ii++){
	if(teile[6][ii]>0 && teile[6][ii]<99999){
	ipTeile.setValue(teile[6][ii]);	//IDFarbe gemäß Tabelle	
	
	x1=(int)teile[0+(int)teile[8][ii]*2][(int)teile[6][ii]];//Andockstelle
	y1=(int)teile[1+(int)teile[8][ii]*2][(int)teile[6][ii]];//Andockstelle
	x2=(int)teile[0+(int)teile[7][ii]*2][ii];//neues Stück
	y2=(int)teile[1+(int)teile[7][ii]*2][ii];//neues Stück
	
	wa.autoOutline(x1, y1, 0, weiss-1);//liegt auf ipTeile
	roi= new PolygonRoi(wa.xpoints,wa.ypoints,wa.npoints, Roi.NORMAL);
	ipTeile.setMask(roi.getMask());
	ipTeile.setRoi(roi.getBounds()); 
	ipTeile.fill(ipTeile.getMask());
	ipTeile.resetRoi();
	impTeile.setProcessor(null, ipTeile);
	wa.autoOutline(x2, y2, 0, weiss-1);//liegt auf ipTeile
	roi= new PolygonRoi(wa.xpoints,wa.ypoints,wa.npoints, Roi.NORMAL);
	ipTeile.setMask(roi.getMask());
	ipTeile.setRoi(roi.getBounds()); 
	ipTeile.fill(ipTeile.getMask());
	ipTeile.resetRoi();
	impTeile.setProcessor(null, ipTeile);
	ipTeile.resetRoi();
}}

//2. Verbindungslinie
for(int ii = 1; ii<teile[0].length;ii++){
	if(teile[6][ii]>0 && teile[6][ii]<99999){
	ipTeile.setValue(teile[6][ii]);	//IDFarbe gemäß Tabelle	
		
	ep1=(int)teile[8][ii];//Endpunkt Andockstelle
	ep2=(int)teile[7][ii];//Endpunkt neues Stück
	ep2neu=Math.abs(ep2-1);//Endpunkt2 verbundenes Stück (alt von neues STück)
	iineu=(int)teile[6][ii];//Farbe der Andockstelle
	x1=(int)teile[0+ep1*2][iineu];//Andockstelle
	y1=(int)teile[1+ep1*2][iineu];//Andockstelle
	x2=(int)teile[0+ep2*2][ii];//neues Stück
	y2=(int)teile[1+ep2*2][ii];//neues Stück
	
	ipTeile.drawLine(x1, y1, x2, y2);//die neue Verbindung
	impTeile.setProcessor(null, ipTeile);
	
	//umsortieren in Teile:
	teile[0+ep1*2][iineu]= teile[0+ep2neu*2][ii];
	teile[1+ep1*2][iineu]= teile[1+ep2neu*2][ii];
	teile[4+ep1][iineu]= teile[4+ep2neu][ii];
	teile[9+ep1*2][iineu]= teile[9+ep2neu*2][ii];
	teile[10+ep1*2][iineu]= teile[10+ep2neu*2][ii];
	teile[6][iineu]= 0;
	for(int i=0;i<teile.length;i++){//alter verbundener Punkt auf Null setzen:
	teile[i][ii]=0;}
}}

impTeile.setProcessor(null,ipTeile);

//------------------------------------------------------------------------------------------
//ursprünglichen Teilstückchen in Teile, die kleiner als Grenzwert, sollen weg
double ll;
ipTeile.setValue(weiss);
for(int ii = 1; ii<teile[0].length;ii++){
	if (teile[0][ii]>0){
	ll=Math.pow(Math.pow(teile[0][ii]-teile[2][ii],2)+Math.pow(teile[1][ii]-teile[3][ii],2),0.5);
	if (ll<5){
	teile[6][ii]=1;}}}//zum Löschen markieren
			



//------------------------------------------------------------------------------------------
//Objekte verlängern 

teile=dehnen(teile,p);//in Teile-Tabelle sind Infos wie Steigung, in p-Matrix Kennzeichnung, ob bereits verbunden
impColl.setProcessor(null,ipColl);
impTeile.setProcessor(null,ipTeile);


//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//LÖSCHEN
//------------------------------------------------------------------------------------------
//Vorarbeiten zum Löschen:
//Löschtabelle: Datensammeln
//Spalte 0 = Löschbefehl
//Spalte 1 = xwert Endpunkt oben
//Spalte 2 = ywert Endpunkt oben
//Spalte 3 = xwert Endpunkt unten
//Spalte 4 = ywert Endpunkt unten
//Spalte 5 = Steigung
//Spalte 6 = Größe
//Spalte 7 = mittlere Breite gem EDM
//Spalte 8 = Standardabweichung der Breite gem EDM normiert
//Spalte 9 = Hilfsspalte für Mittelwertberechnung EDM
//Spalte 10 = Mittelwert Helligkeit
//Spalte 11 = Mittelwert Background
//Spalte 12 = Helligkeitsdifferenz
//Spalte 13 = Spiegelbilder für Größe
//Spalte 14 = welche große Larve wird gekreuzt?
//Spalte 15 = Größe
//Spalte 16 = Kreuzpunkt x-Wert
//Spalte 17 = Kreuzpunkt y-Wert
//Spalte 18 = maximale Helligkeit


double [][] entf = new double[19][teile[0].length]; //Für alle Farben
ipColl.resetRoi(); 
ipColl.min(weiss);

//Gibt es das Objekt noch?
for (int ii =0; ii<teile[0].length; ii++){
if(teile[0][ii]>0){

//1.umsortieren: Endpunkt1 liegt oben=rechts, Endpunkt2 liegt unten=links
	entf[12][ii]=teile[6][ii];//zu löschen, da zu klein
	if(teile[0][ii]> teile[2][ii]){//wenn der erste Endpunkt oben=rechts vom 2. Endpunkt ist
		entf[1][ii]=teile[0][ii];
		entf[2][ii]=teile[1][ii];
		entf[3][ii]=teile[2][ii];
		entf[4][ii]=teile[3][ii];}
	else{//sonst wird umgedreht...
		entf[3][ii]=teile[0][ii];
		entf[4][ii]=teile[1][ii];
		entf[1][ii]=teile[2][ii];
		entf[2][ii]=teile[3][ii];}
	
//2.Steigung berechnen:
	double xdiff= entf[3][ii]-entf[1][ii];
	double ydiff= entf[4][ii]-entf[2][ii];
	double hypo = -Math.sqrt((Math.pow(xdiff, 2.0) + Math.pow(ydiff, 2.0)));
	entf[5][ii]=Math.asin(ydiff/hypo);
	
//3.zur Probe:
ipColl.putPixel((int)entf[1][ii], (int)entf[2][ii], 50);
ipColl.putPixel((int)entf[3][ii], (int)entf[4][ii], 150);
}}
impColl.setProcessor(null,ipColl);


//Größe und sammeln für mittlere Breite
for(y=0;y<h;y++){
for(x=0;x<w;x++){
if(ipTeile.getPixel(x,y)<weiss){
entf[6][ipTeile.getPixel(x,y)]++;//Pixel werden gezählt
if(pEDM[x][y]>0){//nur wenn es was zu berechnen gibt
entf[7][ipTeile.getPixel(x,y)]+=pEDM[x][y];//Aufsummierung für Mittelwertberechnung EDM
entf[8][ipTeile.getPixel(x,y)]+=Math.pow(pEDM[x][y],2.0);//Aufsummierung für Standardwertberechnung EDM
entf[9][ipTeile.getPixel(x,y)]++;//Zählen für Mittelwertberechnung EDM
entf[10][ipTeile.getPixel(x,y)]+=pHell[x][y];//Aufsummierung für Mittelwertberechnung Helligkeit
if(entf[18][ipTeile.getPixel(x,y)]<pHell[x][y])
   entf[18][ipTeile.getPixel(x,y)]=pHell[x][y];//maximale Helligkeit berechnen
entf[11][ipTeile.getPixel(x,y)]+=pBack[x][y];//Aufsummierung für Mittelwertberechnung Background
}}}}

//Mittelwertberechnung
double csquare;
for (int ii =0; ii<entf[1].length; ii++){
if(entf[6][ii]>0){
	csquare = Math.pow(entf[1][ii]-entf[3][ii],2)+Math.pow(entf[2][ii]-entf[4][ii],2);//c^2=a^2+b^2
	entf[6][ii]=Math.max(entf[6][ii], Math.pow(csquare,0.5));
	entf[8][ii]=Math.pow((entf[8][ii]-Math.pow(entf[7][ii],2.0)/entf[9][ii])/(entf[9][ii]-1),0.5);//Standardwertberechnung
	entf[7][ii]=entf[7][ii]/entf[9][ii];//Mittelwertberechnung EDM
	entf[8][ii]=100*entf[8][ii]/entf[7][ii];//Stdev EDM normiert in Prozent
	entf[10][ii]=entf[10][ii]/entf[9][ii];//Mittelwertberechnung Helligkeit
	entf[11][ii]=entf[11][ii]/entf[9][ii];//Mittelwertberechnung Background
	entf[12][ii]=entf[10][ii]-entf[11][ii];//Helligkeitsdifferenz
}}

//Köpfe weg: Knotenpunkte finden
for(y=1;y<h-1;y++){
for(x=1;x<w-1;x++){
	if(ipTeile.getPixel(x,y)<weiss){
	for(int yy=-1;yy<=1;yy++){
	for(int xx=-1;xx<=1;xx++){
		if(ipTeile.getPixel(x+xx,y+yy)<weiss ){
		if (entf[15][ipTeile.getPixel(x,y)]<entf[6][ipTeile.getPixel(x+xx,y+yy)]){//wenn die neue Larve größer als das bisherige ist...
			entf[14][ipTeile.getPixel(x,y)]=ipTeile.getPixel(x+xx,y+yy);//welche Larve wurde gefunden?
			entf[15][ipTeile.getPixel(x,y)]=entf[6][ipTeile.getPixel(x+xx,y+yy)];//welche Größe hat sie?
			entf[16][ipTeile.getPixel(x,y)]=x+xx;//welche x-Koordinaten
			entf[17][ipTeile.getPixel(x,y)]=y+yy;//welche y-Koordinaten
		}
		}
	}}}
}}	



//------------------------------------------------------------------------------------------
//Was wird gelöscht??
//zu den Spiegelbildern:
//gibt es in einer Umgebung einen unverbundenen oberen Endpunkt, 
//der gegensätzlich ist bezüglich Steigung?
//zu den Gesichtern:
//Löschtabelle: Datensammeln
//Spalte 0 = Löschbefehl
//Spalte 1 = xwert Endpunkt oben
//Spalte 2 = ywert Endpunkt oben
//Spalte 3 = xwert Endpunkt unten
//Spalte 4 = ywert Endpunkt unten
//Spalte 5 = Steigung
//Spalte 6 = Größe
//Spalte 7 = mittlere Breite gem EDM
//Spalte 8 = Standardabweichung der Breite gem EDM normiert
//Spalte 9 = Hilfsspalte für Mittelwertberechnung EDM
//Spalte 10 = Mittelwert Helligkeit
//Spalte 11 = Mittelwert Background
//Spalte 12 = Helligkeitsdifferenz (Helligkeit - Background)
//Spalte 13 = Spiegelbilder für Größe
//Spalte 14 = welche große Larve wird gekreuzt?
//Spalte 15 = Größe
//Spalte 16 = Kreuzpunkt x-Wert
//Spalte 17 = Kreuzpunkt y-Wert
//Spalte 18 = maximale Helligkeit

for(int i=1; i<entf[1].length; i++){
if(entf[1][i]==0)
	    entf[0][i]=1;//wenn da, aber kein wirklicher Strich mit Endpunkten
if(entf[1][i]>0 && entf[0][i]==0){//wenn Objekt/Strich überhaupt vorhanden
	    if(entf[0][i]==0 && entf[6][i]<9)
		entf[0][i]=2;//wenn zu klein
	    if(entf[0][i]==0 && entf[6][i]>70)
		entf[0][i]=3;//wenn zu groß
		if(entf[0][i]==0 && Math.abs(entf[5][i])>1.3 && entf[6][i]<20)
		entf[0][i]=4;//wenn parallel und zu klein
		if(entf[0][i]==0 && Math.abs(entf[5][i])> 1.5)
		entf[0][i]=5;//wenn komplett parallel und egal wie groß
		if(entf[0][i]==0 && (entf[2][i]>h-90 || entf[2][i]<0+90) && Math.abs(entf[5][i])<=0.05)
		entf[0][i]=6;//wenn senkrecht und nah zum Rand	
	    if(entf[0][i]==0 && (entf[6][i]/(entf[7][i]*2)*10)<35)
		entf[0][i]=7;//wenn zu dick (dreimal so lang wie breit)
	    if(entf[0][i]==0 && (entf[6][i]/(entf[7][i]*2)*10)>105 || ((entf[6][i]/(entf[7][i]*2)*10)>85 && (entf[7][i]<1.5 || entf[12][i] >75 || entf[8][i]>30)))
		entf[0][i]=8;//(wenn wirklich sehr dünn) oder (wenn dünn und zusätzlich absolut zu dünn oder zu hell oder zuviel Varianz)
	    if(entf[0][i]==0 && entf[7][i]<1.5 && (entf[6][i]/(entf[7][i]*2)*10)>50)
		entf[0][i]=8;//(wenn ganz klein und dünn und dann sehr lang)
	    //if(entf[0][i]==0 && entf[8][i]>=38)//erste Varianzstufe für hohe Dichten
		//entf[0][i]=9;//wenn zuviel Varianz 1
	    if(entf[0][i]==0 && entf[8][i]>=35)//zweite Varianzstufe für geringe dichten
		entf[0][i]=10;//wenn zuviel Varianz 2
	    if(entf[0][i]==0 && entf[12][i]/entf[8][i]*10 < 15)
		entf[0][i]=11;//wenn zu dunkel und zuviel Varianz
	    if(entf[0][i]==0 && entf[12][i]<20 && entf[6][i]<20)
		entf[0][i]=12;//wenn ganz furchtbar dunkel und klein
	    if(entf[0][i]==0 && entf[12][i]<50 && entf[6][i]<15)
		entf[0][i]=13;//wenn dunkel und klein
	    if(entf[0][i]==0 && entf[12][i]<50 && (entf[6][i]/(entf[7][i]*2)*10)>60 && entf[7][i] < 1.5)//im unteren Teil ist sogar 60 noch zu dunkel, aber oben?
		entf[0][i]=14;//wenn zu dunkel und zu dünn relativ zur Länge und zu dünn absolut
	    if(entf[0][i]==0 && entf[15][i]/entf[6][i]>=2 && entf[6][i]<17 && entf[15][i]>35)
	    entf[0][i]=15;//Kopf: wenn große Larve 3* so groß wie kleine und kleine Larve < 15 ist
	    if(entf[0][i]==0 && entf[18][i]>250)
		entf[0][i]=16;//schneeweiße Wasserbläschen weg: wenn wirklich sehr hell
	    if(entf[0][i]==0 && entf[18][i]>220 && entf[7][i]>2  && (entf[6][i]/(entf[7][i]*2)*10)<50)
		entf[0][i]=16;//schneeweiße Wasserbläschen weg: wenn hell, dick und hell und nicht superlang
	    
}}	

for(int i=1; i<entf[1].length; i++){
if(entf[0][i]==0){//wenn immernoch kein Löschbefehl

			for (int jj =1; jj<entf[1].length; jj++){//dann alle Endpunkte absuchen nach
		    //i liegt rechts von jj   && x-Entfernung ist klein	   && y-Entfernung ist klein 	
			double z1=entf[3][i];//xunten vom eventuellen Spiegelbild
			double z2=entf[1][jj];//xoben vom eventuellen Original
			double z3=Math.abs(entf[3][i]-entf[1][jj]);//xDifferenz < 35
			double z4=Math.abs(entf[4][i]-entf[2][jj]);//yDifferenz < 10
			double z8=entf[6][jj]*1;//erlaubte x-Differenz zwischen beiden Larven entspricht Größe der Originallarve		    
			//1. Spiegelbild
			if(z1 > z2 && z3 < z8 && z4 < 10 && entf[0][jj]==0){//..und immernoch da
			double z5=Math.abs(entf[5][i]+entf[5][jj]);//diff Steigung <0.4
			double z6= entf[6][jj]*1.2;//diff Größe <10
			double z7= entf[6][jj]*0.5;//diff Größe <10
			if((z5< 0.4 && entf[6][i]<z6 && entf[6][i]>z7)//Steigung und Größe sind ähnlich
			||(ipOrig.get((int)entf[3][i]+5,(int)entf[4][i])==0)){//wenn nahe Wasseroberfläche
			entf[0][i]=17;//dann als Spiegelbild löschen
			entf[13][i]=1;//als Spiegelbild messen
			entf[13][jj]=1;}}//als Spiegelbild messen
			

}}}

//Löschebefehle: nur noch mal 10
//1 wenn da, aber kein wirklicher Strich mit Endpunkten
//2 wenn zu klein
//3 wenn zu groß
//4 wenn parallel und zu klein
//5 wenn komplett parallel und ein bisschen größer
//6 wenn senkrecht und nah zum Rand	
//7 wenn zu dick
//8 wenn zu dünn
//9 wenn zuviel Varianz Stufe 1
//10 wenn zuviel Varianz Stufe 2
//11 wenn zu dunkel und zuviel Varianz
//12 wenn ganz furchtbar dunkel und klein
//13 wenn dunkel und klein
//14 wenn zu dunkel und zu dünn
//15 Kopf
//16 schneeweiße Bläschen
//17 Spiegelbild

//Jetzt Check: wenn ich alles lösche, wieviele Objekte bleiben? Wenn mehr als 50 Objekte, dann dunkel zurück, sonst streng lassen...
int ObjAnz = 0;
for(int i=1; i<entf[1].length; i++){
	if(entf[0][i]==0) ObjAnz++;}

for(int i=1; i<entf[1].length; i++){
if (ObjAnz>50){
if(entf[0][i]>=11 & entf[0][i]<=14) entf[0][i]=0;}//alles dunkle zurück
//if (ObjAnz>70){
//if(entf[0][i]>=4 & entf[0][i]<=5) entf[0][i]=0;}//bei ganz hohen Dichten werden auch waagerechte Larven akzeptiert
}



impTeile.setProcessor(null,ipTeile);

//--------------------------------------------------------------------------------------------------
//Jetzt wird wirklich gelöscht:

ipColl.resetRoi();
ipColl.min(weiss);

for(int xx=0;xx<w;xx++){
for(int yy=0;yy<h;yy++){
if(ipTeile.getPixel(xx,yy)<weiss){	
	if(entf[0][ipTeile.getPixel(xx,yy)]>0){
		ipColl.putPixel(xx, yy, (int)entf[0][ipTeile.getPixel(xx,yy)]*10);//nur zur Probe...
		ipTeile.putPixel(xx, yy, (int)weiss);}
}
}}
impTeile.setProcessor(null,ipTeile);
impColl.setProcessor(null,ipColl);


//--------------------------------------------------------------------------------------------------
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
impTemp.unlock();
impTemp.changes = false;
impTemp.close();

}
	

	
	
//	------------------------------------------------------------------------------------------
//	die Methoden!!
//	------------------------------------------------------------------------------------------

	
void kleiner (ResultsTable rt, ImagePlus imp, ImageProcessor ip, int aLim){
	int anz = rt.getCounter();
	if (anz == 0)
	return;
			
		float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
		int[] x = new int[anz];
		int[] y = new int[anz];
			
		for (int i=0; i<anz; i++){
			x[i]=(int)rt.getValue("XStart", i);
			y[i]=(int)rt.getValue("YStart", i);	}
		
		WindowManager.setTempCurrentImage(imp);
		for (int ii=0; ii<anz; ii++){
			if (a[ii]<=aLim && ip.get(x[ii], y[ii])==0){
			IJ.doWand(x[ii], y[ii]);
			IJ.run("Clear");}}	
		IJ.run("Select None");
}

/*
void kleiner2 (ResultsTable rt, ImagePlus imp, ImageProcessor ip, int aLim){
	int anz = rt.getCounter();
	if (anz == 0)
	return;
			
		float[] a = rt.getColumn(ResultsTable.AREA); // get area measurements
		int[] x = new int[anz];
		int[] y = new int[anz];
		Roi roi;
		Wand wd = new Wand (ipTeile);
		ipTeile.setValue(weiss);
			
		for (int i=0; i<anz; i++){
			x[i]=(int)rt.getValue("XStart", i);
			y[i]=(int)rt.getValue("YStart", i);}
		
		WindowManager.setTempCurrentImage(imp);
		for (int ii=0; ii<anz; ii++){
			if (a[ii]<=aLim && ip.get(x[ii], y[ii])<weiss){
				wd.autoOutline(x[ii], y[ii], 0, ip.get(x[ii], y[ii]));
				roi= new PolygonRoi(wd.xpoints,wd.ypoints,wd.npoints, Roi.NORMAL);
				ipTeile.setMask(roi.getMask());
				ipTeile.setRoi(roi.getBounds()); 
				ipTeile.fill(ipTeile.getMask());
				ipTeile.resetRoi();
				//impTeile.setProcessor(null, ipTeile);
}}
		
}
*/

double [][] FarbID (){
	
//1. Objekte einfärben
int count=0;
int farbe=1;
Roi roi;
Wand wd = new Wand (ipTeile);
for(int y=1;y<h-1;y++){//laufe die Matrix ab
for(int x=1;x<w-1;x++){
if(ipTeile.getPixel(x, y)==0){//wenn ich einen schwarzen Punkt finde, dann Objekt ID-Farbe einfärben
ipTeile.setValue(farbe);
wd.autoOutline(x, y, 0, 0);
roi= new PolygonRoi(wd.xpoints,wd.ypoints,wd.npoints, Roi.NORMAL);
ipTeile.setMask(roi.getMask());
ipTeile.setRoi(roi.getBounds()); 
ipTeile.fill(ipTeile.getMask());
ipTeile.resetRoi();
farbe++;	
}}}	

//2. Endpunkte in eine 10-Spalten-Tabelle eintragen
double[][] tabelle = new double[13][farbe];//Tabelle für die Endpunkte und ihre Eigenschaften	
//Tabelle für alle farben erzeugen
//Spalte 0 = xwert Endpunkt1
//Spalte 1 = ywert Endpunkt1
//Spalte 2 = xwert Endpunkt2
//Spalte 3 = ywert Endpunkt2


for(int y=0;y<h;y++){//laufe die Matrix ab
for(int x=0;x<w;x++){
p[x][y]=ipTeile.getPixel(x,y);}}//gesäuberte Teilstückchen in Matrix p abspeichern

//Enpunkte herausfinden
for(int y=1;y<h-1;y++){//laufe die Matrix ab
for(int x=1;x<w-1;x++){
if(p[x][y]<weiss){//Objekt
		count = 0;
		for(int yy=-1;yy<=1;yy++){//Prüfung, ob Enpunkt vorliegt
		for(int xx=-1;xx<=1;xx++){
		if(p[x+xx][y+yy]==p[x][y])
		count++;}}
		if (count<=2){//wenn Endpunkt
			if (tabelle[0][p[x][y]]==0){//wenn 1. Endpunkt
				tabelle[0][p[x][y]]=	x;
				tabelle[1][p[x][y]]=	y;}
			else{//wenn 2. Endpunkt
				tabelle[2][p[x][y]]=	x;
				tabelle[3][p[x][y]]=	y;}}
}}}

return tabelle;
}



double[][] steigung (double[][] teile, int[][]p){
	double xdiff, ydiff;
	double  hypo;
	int x,y,neib,cc;
	int xalt=0;
	int yalt=0;
	int xx,yy;
	
for(int ep=0; ep<=1; ep++){//Für beide Endpunkte...
	for (int ii=1; ii < teile[0].length; ii++){
		x = (int)teile[0+ep*2][ii];//Stelle der Endpunkte
		y = (int)teile[1+ep*2][ii];
		
	if(x==0 && y==0){}//Situation gibt es, wenn Skelett Ring ist
	else{
		
		xalt=x;
		yalt=y;
		neib=1;
		cc=0;
		
  //Teilstück 5 Schritte zurück
	while (neib == 1 & cc<5){//solange noch nicht Ende vom Teilstück erreicht
		neib=0;
		for(yy=-1;yy<=1;yy++){//kann man abkürzen??
	    for(xx=-1;xx<=1;xx++){
	    	if(p[x+xx][y+yy]<weiss){
	    		if(((x+xx)==x & (y+yy)==y)||((x+xx)==xalt & (y+yy)==yalt)){}//nichts 
	    		else {
	    		xalt=x;
	    		yalt=y;
	    		x=x+xx;
	    		y=y+yy;
	    		neib++;
	    		cc++;
	    		break;}
	    		}}if(neib==1)break;}
	}

//Ergebnis-Koordinaten vom Tracing: x und y...
	    teile[9+ep*2][ii]=x;//heb Steigungsende auf in Spalten 9 und 10 für EP1 und 11 und 12 für EP2
	    teile[10+ep*2][ii]=y;
		xdiff= x-teile[0+ep*2][ii];
		ydiff= y-teile[1+ep*2][ii];
		
		if (xdiff >= 0) // dann ist x2 rechts von x1			
		hypo = -Math.sqrt((Math.pow(xdiff, 2.0) + Math.pow(ydiff, 2.0)));
		else  // dann ist x2 links von x1
		hypo = Math.sqrt((Math.pow(xdiff, 2.0) + Math.pow(ydiff, 2.0)));
				
		teile[4+ep][ii]=Math.asin(ydiff/hypo);//Steigungseintrag
	}}
}//Endpunkt-Schleife zu
	return teile;	
}



double[][] verbinden(double[][]teile, ImageProcessor ipTeile, ImageProcessor ipColl){
	//Spalte 0 = xwert Endpunkt1
	//Spalte 1 = ywert Endpunkt1
	//Spalte 2 = xwert Endpunkt2
	//Spalte 3 = ywert Endpunkt2
	//Spalte 4 = Steigung Endpunkt 1
	//Spalte 5 = Steigung Endpunkt 2
	//Spalte 6 = ich bin ErgStück: in welcher Farbe ist einzufärben / mit welchem Objekt zu verbinden?
	//Spalte 7 = ErgStück: welcher Endpunkt zur Verbindung?
	//Spalte 8 = AndockStück: welcher Endpunkt zur Verbindung?
	//Spalte 9 = Steigungsende x Endpunkt 1
	//Spalte 10 = Steigungsende y Endpunkt 1
	//Spalte 11 = Steigungsende x Endpunkt 2
	//Spalte 12 = Steigungsende y Endpunkt 2
	
	
	int idwert;
	double xdiff, ydiff;
	double  hypo, steig2;
	double neunzig = Math.PI/180*90;
	double range = 0.45;//nach mehrmals ausprobieren, vielleicht am besten??
	double unt1,ob1,unt2,ob2;
	int xend,yend;
	int out,ep2;
	 
for(int ep = 0; ep<=1; ep++){//Beide Endpunkte der Andockstellen abarbeiten	
	
	for (int ii =1; ii<teile[0].length; ii++){//die gesammelten Endpunkte abarbeiten
	out=0;//kriterium, ob Suche abgebrochen werden kann...
	
		//if(ipColl.get((int)teile[0+ep*2][ii],(int)teile[1+ep*2][ii])== 0){//wenn Endpunkt noch nicht verbunden wurde, (verbunden: Farbe) 
		if(teile[6][ii]== 0){//wenn Endpunkt noch nicht verbunden wurde (entweder ID-Farbe oder 99999) 
		xend=(int)teile[0+ep*2][ii];
		yend=(int)teile[1+ep*2][ii];
	
	if(xend==0 && yend==0){}
	else{
		for (int x=-5; x<=5; x++){
		for (int y=-5; y<=5; y++){
			
			if(ipColl.get(xend+x, yend+y)== 0 && teile[6][ipTeile.get(xend+x, yend+y)]==0){//wenn in der Umgebung von 10 weiterer Endpunkt
				
				idwert=ipTeile.get(xend+x, yend+y);
				ep2=0;//um welches Objekt handelt es sich?
				if(teile[0][idwert]==0 && teile[1][idwert]==0){}
				else{
				if(teile[0][idwert]==xend+x && teile[1][idwert]==yend+y){
				ep2=0;}
				else ep2=1;//welcher der beiden Endpunkte am neuen Objekt soll verbunden werden?
		    		
			if(ipTeile.get(xend+x, yend+y)==ii || ep2-ep==0){}//wenn es eigene Position oder Objekt ist oder Endpunktverteilung nicht gegensätzlich: nichts 
		
			else {
			    			
				if (teile[4+ep][ii]>  neunzig - range){//wenn eigene Steigung fast positiv senkrecht
					unt1 = teile[4+ep][ii]-range;//
					ob1  = neunzig;
					unt2 = -neunzig;
					ob2  = unt1 - 2*(neunzig-range);}
				else if (teile[4+ep][ii]< -neunzig + range){//wenn Steigung fast negativ senkrecht
					unt1 = -neunzig;
					ob1  = teile[4+ep][ii]+range;
					unt2 = ob1 + 2*(neunzig-range);
					ob2  = neunzig;}
				else {
					unt1 = teile[4+ep][ii]-range;//akzeptabler Bereich ermittelt
					ob1  = teile[4+ep][ii]+range;
					unt2 = 99;//Fantasiewert :-)
					ob2  = 99;}
				
			
				double steigneu=0;
				steigneu=teile[4+ep2][idwert];
				
				
				//wenn ähnliche Steigung vorliegt
				if((steigneu>= unt1 && steigneu<= ob1 )||( steigneu>= unt2 && steigneu<= ob2 )){
					
					//die Steigung zwischen den beiden Endpunkten berechnen
					//xdiff= xend-teile[0+ep2*2][idwert];
					//ydiff= yend-teile[1+ep2*2][idwert];
					//Änderung: die äußere Steigung berechnen
					double s=teile[ 9+ep*2][ii];
					s=teile[ 9+ep2*2][idwert];
					s=teile[10+ep*2][ii];
					s=teile[10+ep2*2][idwert];
					
					xdiff= teile[ 9+ep*2][ii]-teile[ 9+ep2*2][idwert];
					ydiff= teile[10+ep*2][ii]-teile[10+ep2*2][idwert];
					
					xend=(int)teile[0+ep*2][ii];
					yend=(int)teile[1+ep*2][ii];
					
					
					if (xdiff >= 0) // dann ist x2 rechts von x1
						hypo = -Math.sqrt((Math.pow(xdiff, 2.0) + Math.pow(ydiff, 2.0)));
					else  // dann ist x2 links von x1
						hypo = Math.sqrt((Math.pow(xdiff, 2.0) + Math.pow(ydiff, 2.0)));
					
					steig2=Math.asin(ydiff/hypo);
	
					//wenn die Steigung der Verbindung ebenfalls passt!!
					if((steig2 >= unt1 && steig2 <= ob1 )||( steig2 >= unt2 && steig2 <= ob2 )){
					double[] connect=ipSez.getLine(xend, yend,teile [0+ep2*2][idwert],teile[1+ep2*2][idwert]);//Verbindung zwischen beiden Endpunkten
					int stop = 0;
					for (int z=0; z<connect.length; z++){
					if(connect[z]==0){
					stop=1; //wenn die Verbindungslinie über schwarzem Zwischenraum liegt
					break;}}
										
					if(stop == 0){//nur wenn Zwischenraum Biomasse ist, gehts weiter
					teile[6][idwert]=ii;//ErgStück: mit welcher id-Farbe muss eingefärbt werden
					teile[6][ii]=99999;//AndockStück: Zeichen, dass bereits verbunden
					teile[7][idwert]=ep2;//ErgStück: welcher der beiden Endpunkte
					teile[8][idwert]=ep;//AndockStück: welcher der beiden Endpunkte
					ipColl.putPixel(xend, yend, ii);//Endpunkt = Andockstelle markieren als verbunden
					ipColl.putPixel(xend+x, yend+y, ii);}}//Endpunkt des einzufärbenden Strichs markieren als verbunden
					out=1;
				}
	    		}}
			if (out==1)break;}
		    if (out==1)break;}//Abbruch der Suche, wenn Kriterium erfüllt
}}}}}			
return teile;	
}



double[][] dehnen(double[][]teile, int [][]p){
int xneu,yneu,xalt,yalt,xend,yend;
double xdiff,ydiff;
int echt;
int multi=2;//das heißt 10 Schritte maximal
double range=0.2;//Farbe darf auf Linie von -20% des Endpunkts bis +80% des Endpunkts abweichen, war vorher auf 20% eingestellt

for(int ep=0; ep<=1;ep++){//beide Endpunkte abarbeiten
	for (int ii =1; ii<teile[0].length; ii++){
	if(teile[0+ep*2][ii]>0 && teile[6][ii]==0){//unverbunden und noch nicht gelöscht...müsste stimmen...
		xalt=(int)teile[0+ep*2][ii];
		yalt=(int)teile[1+ep*2][ii];
		
	echt=ipSez.get(xalt,yalt);
	xdiff=(teile[0+ep*2][ii]-teile[9+ep*2][ii])*multi;
	ydiff=(teile[1+ep*2][ii]-teile[10+ep*2][ii])*multi;
	xneu=xalt+(int)xdiff;
	yneu=yalt+(int)ydiff;
 
	//Linie definieren	
	double[] connect=ipSez.getLine(xalt, yalt, xneu, yneu);
	
	xend = xalt;
	yend = yalt;
	int anzz=connect.length;
	for (int z=0; z<anzz; z++){
	//wenn Rand der Biomasse oder Bildrand oder Linienende erreicht
	if(connect[z]<echt*(1-range) || connect[z]>echt*(1+4*range) || connect[z]==255 || z==anzz-1){
	xend=xalt+(int)(xdiff/anzz*z);
	yend=yalt+(int)(ydiff/anzz*z);
	break;}}
	
	ipTeile.setValue(ii);
	ipTeile.drawLine(xalt, yalt, xend, yend);
	impTeile.setProcessor(null, ipTeile);
	//und den alten Endpunkt mit dem neuen überschreiben
	teile[0+ep*2][ii]=xend;
	teile[1+ep*2][ii]=yend;
	//in p-Matrix alten Endpunkt als verbunden löschen und neuen Endpunkt mit ID-Farbe eintragen.
		
	}}}
	return teile;}


}





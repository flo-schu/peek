import ij.IJ;
import ij.ImagePlus;
import ij.WindowManager;
import ij.gui.Roi;
import ij.gui.Wand;
import ij.measure.Measurements;
import ij.measure.ResultsTable;
import ij.plugin.PlugIn;
import ij.plugin.filter.Analyzer;
import ij.plugin.filter.ParticleAnalyzer;
import ij.process.BinaryProcessor;
import ij.process.Blitter;
import ij.process.ImageProcessor;


public class Xd1_ implements PlugIn, Measurements {

	/** Display results in the ImageJ console. */
	public static final int SHOW_RESULTS = 1, SHOW_OUTLINES = 4, MIN =12, SHOW_SIZE_DISTRIBUTION = 16, DIFFERENCE=8, COPY=0;
	public static final int SHOW_PROGRESS = 32, CLEAR_WORKSHEET = 64, RECORD_STARTS = 128,DISPLAY_SUMMARY = 256, SHOW_NONE = 512,BLACK = -16777216;
	//public static final int AREA=0, MAJOR = 15, MINOR = 16 ;
	protected static final int NOTHING=0,OUTLINES=1,MASKS=2,ELLIPSES=3;
		
	
	int oben;
	int[] kleber=new int [2];
	ImagePlus imp1, imp2, imp3, imp1_, imp2_, imp3_,impBlue;
	ImageProcessor ip,ip1,ip2,ip3,ipBlue;
	BinaryProcessor bps;
	int w,h;
	int measurements,options;
	int AbzCulex=30;

	
	
	ResultsTable rt = new ResultsTable();
	
//--------------------------------------------------------------------------------------	
	public void run(String arg) {
		if (IJ.versionLessThan("1.37s"))
			return;
	//Fläche messen, da Voraussetzung für Lageberechnung
	measurements = Analyzer.getMeasurements(); // defined in Set Measurements dialog
	Analyzer.setMeasurements(0);
	measurements |= AREA+PERIMETER+ELLIPSE+CIRCULARITY+MEAN;;  //make sure area is measured
	options = CLEAR_WORKSHEET+RECORD_STARTS;//+SHOW_NONE;
	Analyzer.setMeasurements(measurements);
	ParticleAnalyzer pa = new ParticleAnalyzer(options, measurements, rt, 0, 99999999);
	
		imp1  = WindowManager.getImage("0");
		imp2  = WindowManager.getImage("1");
		imp3  = WindowManager.getImage("2");
		ip1 = imp1.getProcessor();
		ip2 = imp2.getProcessor();
		ip3 = imp3.getProcessor();
		
		ip = ip1.duplicate();
		w=imp1.getWidth();
		h=imp1.getHeight();
		
		IJ.run("XB ");
		
		impBlue =  WindowManager.getImage("Blue");
		ipBlue = impBlue.getProcessor();
		ipBlue.setValue(255);
		ipBlue.drawLine(0, 0, w-1, 0);//Fehler in ImageJ, ab und zu selektiert wand sonst das weiße...
		impBlue.setProcessor(null, ipBlue);
		rt.reset();
		pa.analyze(impBlue);//Lage des blauen Bandes berechnen
		kleber = ortgOb (ipBlue, rt);
		impBlue.unlock();
		impBlue.changes = false;
	    impBlue.close();	
		
	
		//die Wasseroberfläche bestimmen
		ip=ip.convertToByte(false);
		oben = (int)kleber[1];
		for(int kk = 10; kk<100; kk++){
			oben=oben-kk;
			if (ip.get(oben, kleber[0])< 190)//wenn es unter dem blau sehr hell ist, weil Wasser fehlt...
				break;	}

		oben = oben-AbzCulex; //nochmal was abziehen wegen der Mücken
	

	 	
		//einzelne Fotos zuschneiden
		ip = ip1.duplicate();
		schnitt (ip1, 0, oben, h, w);
		schnitt (ip2, 0, oben, h, w);
		schnitt (ip3, 0, oben, h, w);
		schnitt (ip, 0, oben, h,w);
		imp1.setProcessor(null,ip1);	
		imp2.setProcessor(null,ip2);
		imp3.setProcessor(null,ip3);//hat geklappt ip und imp ist richtig
		
		//-------------------------------------------------------------------------------------------------
		//Fotos voneinander abziehen
		ip.copyBits(ip2, 0, 0, Blitter.MIN);
		ip.copyBits(ip3, 0, 0, Blitter.MIN);
		ip1.copyBits(ip, 0, 0, Blitter.DIFFERENCE);
		imp1.setProcessor(null,ip1);
		ip2.copyBits(ip, 0, 0, Blitter.DIFFERENCE);
		imp2.setProcessor(null,ip2);
		ip3.copyBits(ip, 0, 0, Blitter.DIFFERENCE);
		imp3.setProcessor(null,ip3); //hat geklappt
		imp1_ = new ImagePlus ("o0", ip1);
		imp2_ = new ImagePlus ("o1", ip2);
		imp3_ = new ImagePlus ("o2", ip3);
		imp1_.show();
		imp2_.show();
		imp3_.show();



}

	
	
int []ortgOb(ImageProcessor ip, ResultsTable rt){
		int []grenze = new int [2];
		int xwert =w;
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
				if( xx[jj]< xwert)
					xwert = xx[jj];}
				
		grenze[0]=h/2;
		grenze[1]=xwert;

return grenze;}



	void schnitt (ImageProcessor ip, int unten, int oben, int h, int w){
		
		ip.setValue(10);
		Roi roiU = new Roi (0,0,unten,h);
		ip.setRoi(roiU);
		ip.fill();
		ip.resetRoi();
		Roi roiO = new Roi(oben,0,w-oben,h);
		ip.setRoi(roiO);
		ip.fill();
		ip.resetRoi();}	
	
}

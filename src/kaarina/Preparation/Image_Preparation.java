import ij.IJ;
import ij.ImagePlus;
import ij.WindowManager;
import ij.gui.GenericDialog;
import ij.gui.Roi;
import ij.io.FileSaver;
import ij.io.SaveDialog;
import ij.measure.Measurements;
import ij.plugin.PlugIn;
import ij.process.ColorProcessor;
import ij.process.ImageProcessor;

import java.awt.Button;
import java.awt.FlowLayout;
import java.awt.Panel;
import java.awt.TextField;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FilenameFilter;
import java.util.Vector;



public class Image_Preparation implements PlugIn, Measurements, ActionListener {

	
	/** Display results in the ImageJ console. */
	public static final int SHOW_RESULTS = 1, SHOW_OUTLINES = 4, MIN =12, SHOW_SIZE_DISTRIBUTION = 16, DIFFERENCE=8, COPY=0;
	public static final int SHOW_PROGRESS = 32, CLEAR_WORKSHEET = 64, RECORD_STARTS = 128,DISPLAY_SUMMARY = 256, SHOW_NONE = 512;
	public static final int MAJOR = 15, MINOR = 16, BLACK = -16777216, GET_BOUNDS = 375,RED_LUT=0;
	protected static final int NOTHING=0,OUTLINES=1,MASKS=2,ELLIPSES=3;
	static final int R=0, G=1, B=2;
		
	
	ImagePlus imp, impBlue;
	ImageProcessor ip, ip2;
	ColorProcessor cp;
	int w,h;
	double verh,Fak;
	GenericDialog gd;
	Button browse1, browse2;
	String rotation, scaling, zoom;
	double start=0, end=149;
	int anzFotos=0;
	String bild;
	int Change;
	
	static String path = "";
	
	
	
//	--------------------------------------------------------------------------------------
	
	public void run(String arg) {
		
		System.out.print("input data.\n");
		getData2();//User sagt über Maske, was er will...
		
		System.out.print("starting.\n");
		File ordner = new File(path);
		FilenameFilter filter1 = new FilenameFilter(){
	          public boolean accept(File ordner, String messung){
	              return messung.startsWith("#");}};//nur die Messtermine sollen abgearbeitet werden
	     		
		String[] termine = ordner.list(filter1);
		
		
		for (int qq=0; qq<termine.length; qq++) {//die größte Schleife zum abarbeiten aller Ordner
			String tag = termine[qq];
		     
		    anzFotos=(int)(end-start+1); 
	 
		      
		    for (int zz=(int)start; zz<=(int)end; zz++){ 
		    	Change = 0;//ich zähle die Veränderungen, nur wenn geändert wird, soll auch neu in jpg gespeichert werden.
							
//				System.out.println(IJ.currentMemory()); 
				int min_freeMemory = 50;
				int freeMemory;
				for (int i=0; i<100; i++) {
					System.gc();// run garbage collector:
					freeMemory = 100 - (int)(IJ.currentMemory() * 100 / IJ.maxMemory());// MemoryCheck:
					if (freeMemory >= min_freeMemory) {
						break;
						}
					}
//				System.out.println(IJ.currentMemory());	
					
			    IJ.open(path + "\\" +tag+ "\\" + zz + ".jpg");
				imp  = WindowManager.getImage(zz + ".jpg");
				ip = imp.getProcessor();
				w = imp.getWidth();
				h = imp.getHeight();
				    
				if(ip.get(0, 0)==255){
					System.out.print("i didnt change anything");
					imp.unlock();
					imp.changes = false;
					imp.close();
				}
				else{
				
					if(rotation == "1 step left"){
						ip=ip.rotateLeft();
						imp.setProcessor(null,ip);
						Change++;
					}
					if(rotation == "1 step right"){
						ip=ip.rotateRight();
						imp.setProcessor(null,ip);
						Change++;
						System.out.print("rotation one step right.\n");
					}	
							
					if(rotation == "All to the right"){	
						double w2,h2;
						w2 = imp.getWidth();
						h2 = imp.getHeight();
						verh=Math.round(w2/h2 * 10.) / 10.;
						
						if (verh < 1){
							ip=ip.rotateRight();
							w=(int)h2;//Falls rotiert, dann natürlich auch die Seitenlängen vertauschen...
							h=(int)w2;
							//imp.setProcessor(null,ip);
							Change++;
						}//wenn das Bild aufrecht steht, dann erstmal nach rechts kippen
								
						//Jetzt prüfen, ob der blaue Streifen links oder rechts ist
						cp=(ColorProcessor)ip;
						int Col=0;
						int Anz=0;
						int Mean;
						int[]yp={h/5*1,h/5*2,h/5*3,h/5*4};
						int[]RGB = new int [3];
					    int[]B1={0,100,0,255,150,255};
					    int[]B2={0,200,0,255,230,255};
					    int[]B3={0,14,0,255,64,255};
					    				    
						for(int r = 1; r < 4; r++){
							for(int x = 0; x < w; x++){
								int y=yp[r];
								cp.getPixel(x,y,RGB);
								if((RGB[R]>=B1[0] & RGB[R]<=B1[1])&(RGB[G]>=B1[2] & RGB[G]<=B1[3])&(RGB[B]>=B1[4]&RGB[B]<=B1[5])||
								   (RGB[R]>=B2[0] & RGB[R]<=B2[1])&(RGB[G]>=B2[2] & RGB[G]<=B2[3])&(RGB[B]>=B2[4]&RGB[B]<=B2[5])||
								   (RGB[R]>=B3[0] & RGB[R]<=B3[1])&(RGB[G]>=B3[2] & RGB[G]<=B3[3])&(RGB[B]>=B3[4]&RGB[B]<=B3[5])){
								Col=Col+x;
								Anz=Anz+1;
								}
							}
						}
						
						Mean=Col/Anz;
						if(Mean < w/2){
							ip=ip.rotateRight();
							ip=ip.rotateRight();
							Change++;
						}//Wenn der blaue Streifen links ist, dann 2X nach rechts drehen.
						imp.setProcessor(null,ip);
						
					}
					
					if(scaling == "Yes"){
						double w2,h2;
						w2 = imp.getWidth();
						h2 = imp.getHeight();
						verh=Math.round(w2/h2 * 10.) / 10.;
						//Fak = 2048./w2;
						System.out.println("height: " + h2); //changes florian
						System.out.println("width: " + w2);
						System.out.println("ratio: " + verh);
	//					pressAnyKeyToContinue();     // changes florian
						
						if (verh == 1.3 & w > 2048){	
							ip2=ip.resize(2048);
							imp.setProcessor(null,ip2);
							Change++;
						// scaling from Florian's Camera
						} else if (verh == 1.5 & w > 2048){	
							System.out.print("scale florians image.\n");

							double trim = w2 - (h2 * 1.3);
							Roi croparea = new Roi((int)trim/2, 0, (int)(w2-trim), h2);
							System.out.println(croparea);
//							ip2=imp.getProcessor();
							System.out.println(ip);
							ip=imp.getProcessor();
							ip.setRoi(croparea);
							ip2=ip.crop();
							ip2.resetRoi();					
							ip2=ip2.resize(2048);
							System.out.println("height: " + ip2.getHeight());
							System.out.println("width: " + ip2.getWidth());
							System.out.println("ratio: " + Math.round(ip2.getWidth()/ip2.getHeight() * 10.) / 10.);
							imp.setProcessor(null,ip2);
							System.out.println(imp);
							Change++;
						}
						
						
					}
					
			//Bei Ida war die Umrechnung noch mit 1948
			//Bei Renato jetzt auf 1764
//						if(zoom == "Yes" & imp.getPixel(0, 0)[1]> 0 & imp.getWidth()==2048){
						if(zoom == "Yes" & imp.getWidth()==2048){
							System.out.println("zooming...");
							ip=imp.getProcessor();
							ip2=ip.resize(1764); 
							imp.setProcessor(null,ip2);
							IJ.run("Canvas Size...", "width=2048 height=1536 position=Center zero");
							Change++;
						}
				
					
					if(Change>0){
						FileSaver.setJpegQuality(95);
						new FileSaver(imp).saveAsJpeg(path + "\\" +tag+ "\\" + zz + ".jpg");
					}//alt wird überschrieben
				
					imp.unlock();
					imp.changes = false;
					imp.close();			
				}
		    }
		}
	}	
		
    void getData2(){
	    gd = new GenericDialog("Settings");
	    
	    String[] choices = {"No","All to the right","1 step left", "1 step right"};
	    gd.addChoice("Rotation? Please not too often", choices, "All to the right");
	    gd.addMessage("");
	    
	    String[] choices2 = {"No","Yes"};
	    gd.addChoice("Scaling? No Undo possible!!!", choices2, "Yes");
	    gd.addMessage("");
	    gd.addMessage("");
	    
	    String[] choices3 = {"No","Yes"};
	    gd.addChoice("Zoom? No Undo possible!!!", choices3, "Yes");
	    gd.addMessage("");
	    gd.addMessage("");
	    
		gd.addStringField("Path to the folder of photos:", path, 30);
		gd.addPanel(makePanel(gd, 2));
		gd.addMessage("");
		gd.addMessage("");
		
		gd.addMessage("Limits of photo analysis:");
		gd.addNumericField("From photo:", 0, 0);
		gd.addNumericField("to photo:", 239, 0);
		
		gd.showDialog();
		
		rotation = gd.getNextChoice();
		scaling = gd.getNextChoice();	
		zoom = gd.getNextChoice();
		path = gd.getNextString();
		start = gd.getNextNumber();
//		end = new File(path).list().length; // get file number
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
	
	private void pressAnyKeyToContinue()
	 { 
	        System.out.println("Press Enter key to continue...");
	        try
	        {
	            System.in.read();
	        }  
	        catch(Exception e)
	        {}  
	 }
		
}

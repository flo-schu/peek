import ij.ImageJ;
import ij.plugin.PlugIn;

/**
  Beispiel-PlugIn zur Erzeugung von Bildern
*/

public class XM1_20191028 implements PlugIn {

	final static String[] choices = {
		"Schwarzes Bild", 
		"Gelbes Bild", 
		"Schwarz/Wei� Verlauf", 
		"horiz. Schwarz/Rot vert. Schwarz/Blau Verlauf", 
		"Franz�sische Fahne",
		"Japanische Fahne",
		"Japanische Fahne mit weichen Kanten",
		"..."};
	
	

	public static void main(String args[]) {
		new ImageJ(); }
		
	public void run(String arg) {}

}
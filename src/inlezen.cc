#include "inlezen.h"

void Inlezen::readInInformation(string dir) {
   ifstream file(dir.c_str(), ios::in);
   string line;


   if (!file.is_open()) {
      cout << "konker::Inlezen.readInInformation(" << dir << ") Error! Could not open informationFile..\n";
      exit(0);
   }
   //zo iets
    /*
   while (getline(file, line) && line != "Dataset");
   parseDatasetSettings(file);
   while (getline(file, line) && line != "General");
   parseGeneralSettings(file);
   while (getline(file, line) && line != "Codebook");
   parseCodebookSettings(file);
   while (getline(file, line) && line != "FeatureExtractor");
   parseFeatureExtractorSettings(file);
   while(getline(file, line) && line != "CleanDescriptor");
   parseCleanDescrSettings(file);
   while (getline(file, line) && line != "ImageScanner");
   parseImageScannerSettings(file);
   while (getline(file, line) && line != "MLPController");
   parseMLPControllerSettings(file);
   while (getline(file, line) && line != "MLP");
   parseMLPSettings(file);
   while (getline(file, line) && line != "SVM");
   parseSVMSettings(file);
   while (getline(file, line) && line != "LinNet");
   parseLinNetSettings(file);
   while (getline(file, line) && line != "ConvSVM");
   parseConvSVMSettings(file);
   // parse values:
   */

   file.close();
}

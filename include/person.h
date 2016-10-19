#ifndef PERSON_H
#define PERSON_H

#include <iostream>
#include <vector>


using namespace std;
   class Person{
       string name;
       string location;
       bool male;
       bool home;
       int teamPlaying;
       int verzameltijd;
       int reistijd;
       vector<bool> beschikbaarheid;
       
       Person(string name,int verzameltijd);
       Person(string name,int verzameltijd,int reistijd);

   };
#endif
#include <stdlib.h>
#include <fstream>
#include <iostream>
#include "map.h"


using namespace std;
int main()
{
  map *a = new map(30,-1);
  //a->set(15,15,-1);
  a->set(16,14,1);
  a->set(17,13,1);
  a->set(18,12,1);
  a->set(19,11,1);
  for (int i = 0;i<1;i++){
    a->printMap();
  }
  
  return 0;
}

#include <stdlib.h>
#include <fstream>
#include <iostream>
#include "map.h"


using namespace std;
int main()
{
  map *a = new map(30,-1);
  //a->set(15,15,-1);
  for (int i = 0;i<1;i++){
    a->printMap();
  }
  cout << a->returnValidPos().arr[0]<< endl;
  cout << a->returnValidPos().arr[1]<< endl;
  return 0;
}

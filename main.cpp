#include <stdlib.h>
#include <fstream>
#include <iostream>
#include "map.h"
#include <random>

using namespace std;
int main()
{
  map *a = new map(30, -1);
  // a->set(15,15,-1);
  for (int i = 0; i < 1; i++)
  {
    int won = 0;
    while(!won){
      
      if(a->checkWin(1,2,1)){
        won = 1;
        continue;
      }
    }
    a->clear();
  }
  sizeAndArrPointer validPos = a->getValidPos();
  random_device rd;                                                   // Only used once to initialise (seed) engine
  mt19937 rng(rd());                                                  // Random-number engine used (Mersenne-Twister in this case)
  uniform_int_distribution<int> uni(0, (int)(validPos.size / 2) - 1); // Guaranteed unbiased

  auto random_integer = uni(rng);
  cout << validPos.arr[random_integer*2] << "," << validPos.arr[random_integer*2+1] << endl;
  return 0;
}

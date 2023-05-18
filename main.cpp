#include <stdlib.h>
#include <fstream>
#include <iostream>
#include "map.h"
#include <random>

using namespace std;
int main()
{
  map *a = new map(30, -1);
  sizeAndArrPointer validPos = a->getValidPos();
  random_device rd;                                                   // Only used once to initialise (seed) engine
  mt19937 rng(rd());                                                  // Random-number engine used (Mersenne-Twister in this case)
  uniform_int_distribution<int> *uni = new uniform_int_distribution<int>(0, (int)(validPos.size / 2) - 1); // Guaranteed unbiased

  auto random_integer = uni->operator()(rng);

  // a->set(15,15,-1);
  for (int i = 0; i < 1000; i++)
  {
    int won = 0;
    int val = 0;
    while(!won){
      validPos = a->getValidPos();
      uni = new uniform_int_distribution<int>(0, (int)(validPos.size / 2) - 1); // Guaranteed unbiased
      val = a->getCurrentPlayer();
      random_integer = uni->operator()(rng);
      a->set(validPos.arr[random_integer*2],validPos.arr[random_integer*2+1],val);
      if(a->checkWin(validPos.arr[random_integer*2],validPos.arr[random_integer*2+1],val)){
        won = 1;
        //cout << "Winner is:" << val << endl;
        continue;
      }
      validPos = a->getValidPos();
      uni = new uniform_int_distribution<int>(0, (int)(validPos.size / 2) - 1); // Guaranteed unbiased
      val = a->getCurrentPlayer();
      random_integer = uni->operator()(rng);
      a->set(validPos.arr[random_integer*2],validPos.arr[random_integer*2+1],val);
      if(a->checkWin(validPos.arr[random_integer*2],validPos.arr[random_integer*2+1],val)){
        won = 1;
        //cout << "Winner is:" << val << endl;
        continue;
      }
    }
    //a->printMap();
    a->clear();
  }
  return 0;
}

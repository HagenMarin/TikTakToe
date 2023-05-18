#include <stdlib.h>
#include <fstream>
#include <iostream>
#include "map.h"
#include <random>

using namespace std;

sizeAndArrPointer useStrat(map a)
{
  sizeAndArrPointer validPos = a.getValidPos();
  for (int i = 0; i < validPos.size / 2; i++)
  {
    if (a.checkWin(validPos.arr[i * 2], validPos.arr[i * 2 + 1], a.getCurrentPlayer()))
    {
      int x = validPos.arr[i * 2];
      int y = validPos.arr[i * 2 + 1];
      validPos.arr = new int[2];
      validPos.size = 2;
      validPos.arr[0] = x;
      validPos.arr[1] = y;
    }
  }
  return validPos;
}

int main()
{
  map *a = new map(30, -1);
  sizeAndArrPointer validPos = a->getValidPos();
  random_device rd;                                                                                        // Only used once to initialise (seed) engine
  mt19937 rng(rd());                                                                                       // Random-number engine used (Mersenne-Twister in this case)
  uniform_int_distribution<int> *uni = new uniform_int_distribution<int>(0, (int)(validPos.size / 2) - 1); // Guaranteed unbiased

  auto random_integer = uni->operator()(rng);

  // a->set(15,15,-1);
  int winRatio = 0;
  for (int i = 0; i < 100000; i++)
  {
    int won = 0;
    int val = 0;
    while (!won)
    {
      validPos = useStrat(*a);
      if (validPos.size == 2)
      {
        a->set(validPos.arr[0], validPos.arr[1], a->getCurrentPlayer());
      }
      else
      {
        uni = new uniform_int_distribution<int>(0, (int)(validPos.size / 2) - 1); // Guaranteed unbiased
        val = a->getCurrentPlayer();
        random_integer = uni->operator()(rng);
        a->set(validPos.arr[random_integer * 2], validPos.arr[random_integer * 2 + 1], val);
      }

      if (a->checkWin(validPos.arr[random_integer * 2], validPos.arr[random_integer * 2 + 1], val))
      {
        won = 1;
        // cout << "Winner is:" << val << endl;
        continue;
      }
      validPos = a->getValidPos();
      uni = new uniform_int_distribution<int>(0, (int)(validPos.size / 2) - 1); // Guaranteed unbiased
      val = a->getCurrentPlayer();
      random_integer = uni->operator()(rng);
      a->set(validPos.arr[random_integer * 2], validPos.arr[random_integer * 2 + 1], val);
      if (a->checkWin(validPos.arr[random_integer * 2], validPos.arr[random_integer * 2 + 1], val))
      {
        won = 1;
        // cout << "Winner is:" << val << endl;
        continue;
      }
    }
    //cout << "Winner is:" << val << endl;
    winRatio += val;
    // a->printMap();
    a->clear();
  }
  cout << "The win ratio is:" << winRatio << endl;
  return 0;
}

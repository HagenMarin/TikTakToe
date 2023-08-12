#include <stdlib.h>
#include <fstream>
#include <iostream>
#include "map.h"
#include <random>
#include <cstdlib>


using namespace std;

vector<int> useStrat(map a)
{
  vector<int> validPos = a.getValidPos();
  vector<int> strat_moves;
  for (int i = 0; i < validPos.size() / 2; i++)
  {
    //cout << "3" << endl;
    if (a.checkWin(validPos[i * 2], validPos[i * 2 + 1], a.getCurrentPlayer()))
    {
      int x = validPos[i * 2];
      int y = validPos[i * 2 + 1];
      strat_moves.push_back(x);
      strat_moves.push_back(y);
      return strat_moves;
    }
  }
  for (int i = 0; i < validPos.size() / 2; i++)
  {
    //cout << "Checking:" << a.getCurrentPlayer() * -1 << endl;
    
    if (a.checkWin(validPos[i * 2], validPos[i * 2 + 1], a.getCurrentPlayer() * -1)){
      //cout << a.checkWin(validPos.arr[i * 2], validPos.arr[i * 2 + 1], a.getCurrentPlayer() * -1) << endl;
      int x = validPos[i * 2];
      int y = validPos[i * 2 + 1];
      //cout << "found defending move at:" << x << "," << y << ", Player:" << a.getCurrentPlayer() * -1 << endl;
      strat_moves.push_back(x);
      strat_moves.push_back(y);
      return strat_moves;
    }
  }
  for (int i = 0; i <validPos.size()/2;i++){
    int x = validPos[i * 2];
    int y = validPos[i * 2 + 1];
    strat_moves.push_back(x);
    strat_moves.push_back(y);
  }
  return strat_moves;
}

int main()
{
  map *a = new map(30, -1);
  vector<int> validPos = a->getValidPos();
  

  auto random_integer = (int)(static_cast<double>(std::rand() * ((validPos.size() / 2) - 1)) / RAND_MAX); 

  // a->set(15,15,-1);
  int winRatio = 0;
  for (int i = 0; i < 10; i++)
  {
    int won = 0;
    int val = 0;
    int x;
    int y;
    while (!won)
    {
      //cout << a->getCurrentPlayer() << endl;
      val = a->getCurrentPlayer();
      validPos = useStrat(*a);
      if (validPos.size() == 2)
      {
        a->set(validPos[0], validPos[1], a->getCurrentPlayer());
        x = validPos[0];
        y = validPos[1];
      }
      else
      {
        
        random_integer = (int)(static_cast<double>(std::rand() * ((validPos.size() / 2) - 1)) / RAND_MAX); 
        a->set(validPos[random_integer * 2], validPos[random_integer * 2 + 1], val);
        x = validPos[random_integer * 2];
        y = validPos[random_integer * 2 + 1];
      }
      if (a->checkWin(x, y, val))
      {
        won = 1;
        //cout << "Winner is:" << val << endl;
        continue;
      }
      validPos = a->getValidPos();
      val = a->getCurrentPlayer();
      random_integer = (int)(static_cast<double>(std::rand() * ((validPos.size() / 2) - 1)) / RAND_MAX); 
      a->set(validPos[random_integer * 2], validPos[random_integer * 2 + 1], val);
      if (a->checkWin(validPos[random_integer * 2], validPos[random_integer * 2 + 1], val))
      {
        won = 1;
        // cout << "Winner is:" << val << endl;
        continue;
      }
    }
    cout << "Winner is:" << val << endl;
    winRatio += val;
    a->printMap();
    a->clear();
  }
  cout << "The win ratio is:" << winRatio << endl;
  return 0;
}

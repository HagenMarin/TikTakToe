#ifndef __LIST_SET_H__
#define __LIST_SET_H__

#include <stdio.h>
#include <iostream>

using namespace std;

struct sizeAndArrPointer{
    int size;
    int *arr;
};

class map
{
private:

    int *mapArr;
    int size = 0;
    int currentPlayer;
    char symbols[2] = {'O','X'};

    int* deep_copy_list(int* a, int length){
        int* temp = new int[length];
        for (int i = 0;i<length;i++){
            temp[i] = a[i];
        }
        return temp;
    }

public:
    
    map(int mapSize=10,int startingPlayer = -1){
        currentPlayer = startingPlayer;
        size = mapSize;
        mapArr = new int[size*size];
        clear();
        
    }
    map(const map &m) { 
        this->size = m.size;
        this->currentPlayer = m.currentPlayer;
        this->mapArr = deep_copy_list(m.mapArr,m.size*m.size);
    }
    // destructor
    ~map()
    {
        delete mapArr;
    }

    map operator=(const map &m){
        this->mapArr = deep_copy_list(m.mapArr,m.size*m.size);
        return *this;
    }

    int getCurrentPlayer(){
        return currentPlayer;
    }

    int checkValidity(int index1, int index2){
        if(mapArr[index1*size+index2]){
            return 0;
        }
        for(int i = -1;i<2;i++){
            if(index1+i<0||index1+i>size-1){
                continue;
            }
            for(int n = -1;n<2;n++){
                if(index2+n<0||index2+n>size-1){
                    continue;
                }
                if(mapArr[(index1+i)*size+index2+n]){
                    return 1;
                }
            }
        }
        return 0;
    }

    int checkWin(int index1,int index2,int val){
        int count = 0;
        for (int i = max(-4,-index2);i<min(5,size-index2);i++){
            if(mapArr[index1*size+index2+i]!=val){
                count=0;
            }else{
                count++;
                if(count==5){
                    return 1;
                }
            }

        }
        count = 0;
        for (int i = max(-4,-index1);i<min(5,size-index1);i++){
            if(mapArr[(index1+i)*size+index2]!=val){
                count=0;
            }else{
                count++;
                if(count==5){
                    return 1;
                }
            }
        }
        count = 0;
        for (int i = max(-index2,max(-4,-index1));i<min(min(5,size-index1),size-index2);i++){
            if(mapArr[(index1+i)*size+index2+i]!=val){
                count=0;
            }else{
                count++;
                if(count==5){
                    return 1;
                }
            }

        }
        count = 0;
        for (int i = max(max(-4,-index1),-(size-index2));i<min(min(5,size-index1),index2);i++){
            if(mapArr[(index1+i)*size+index2-i]!=val){
                count=0;
            }else{
                count++;
                if(count==5){
                    return 1;
                }
            }

        }
        return 0;
    }

    sizeAndArrPointer getValidPos() {
        int sizeOfArr = 0;
        for (int i = 0;i<size;i++){
            for(int n = 0;n<size;n++){
                if(checkValidity(i,n)){
                    sizeOfArr++;
                            
                        
                    
                }
            }
        }
        int* temp = new int[sizeOfArr*2];
        int counter = 0;
        for (int i = 0;i<size;i++){
            for(int n = 0;n<size;n++){
                if(checkValidity(i,n)){
                    temp[counter] = i;
                    counter++;
                    temp[counter] = n;
                    counter++;
                }
            }
        }
        sizeAndArrPointer a;
        a.arr = temp;
        a.size = sizeOfArr*2;
        return a;
    }
    
    void printMap()
    {
        string line = "";
        int emptyLine = 1;
        for (int i = 0; i < size; i++)
        {
            emptyLine = 1;
            line = "|";
            for (int n = 0; n < size; n++)
            {
                if(!mapArr[i * size + n]){
                    line += "  ";
                }else{
                    line+= symbols[max(0,mapArr[i * size + n])];
                    line+= " ";
                    emptyLine = 0;
                }
                
            }
            line += "|";
            if(!emptyLine){
                cout << line << endl;
            }
        }
        
    }
    

    map set(int index1, int index2, int val){
        if(val!=currentPlayer){
            cout << "Warning: Current Player is not equal to set Player" << endl;
        }
        if(index1>size || index2>size){
            throw std::out_of_range("Index out of range");
        }
        if(!checkValidity(index1,index2)){
            throw std::invalid_argument("Invalid Move");
        }
        this->mapArr[index1*size+index2]=val;
        /*if(checkWin(index1,index2,val)){
            printMap();
            clear();
        }*/
        currentPlayer *= -1;
        return *this;
    }
    map clear(){
        for(int i = 0;i<size*size;i++){
            mapArr[i] = 0;
        }
        mapArr[(int)(size/2)*size+(int)(size/2)]=currentPlayer*-1;
        return *this;
    }
};

#endif
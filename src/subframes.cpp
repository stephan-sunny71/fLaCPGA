/* subframe.cpp - Read in FLAC subframes */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include <vector>

#include "subframes.hpp"

#include "bitreader.hpp"


/***********************************
 * SUB FRAME HEADER ****************
 * *********************************/

FLACSubFrameHeader::FLACSubFrameHeader(){
    this->zeroBit = 1;
    this->subFrameType = 0b000100; //Reserved, so this should never occur
    this->wastedBitsPerSample = 0;
}

void FLACSubFrameHeader::print(FILE *f){
    fprintf(f, "\
Zero Bit: %d\n\
Sub-Frame type: %x\n\
Wasted Bits: %d\n\n", this->zeroBit, this->subFrameType, this->wastedBitsPerSample);
}

int FLACSubFrameHeader::read(FileReader *fr){
    fr->read_bits_uint8(&this->zeroBit, 1);
    fr->read_bits_uint8(&this->subFrameType, 1);
    uint8_t x;
    fr->read_bits_uint8(&x, 1);
    if (x){
        fr->read_bits_unary(&this->wastedBitsPerSample);
    }
}



/*************************************
 * VERBATIM SUBFRAME *****************
 *************************************/

FLACSubFrameVerbatim::FLACSubFrameVerbatim(uint8_t bitsPerSample, uint32_t blockSize){
    this->bitsPerSample = bitsPerSample;
    this->blockSize = blockSize;
}

int FLACSubFrameVerbatim::read(FileReader *fr){
    data = (uint32_t*)malloc(sizeof(uint32_t) * this->blockSize);
    
    if (this->bitsPerSample == 8){
        fr->read_file(data, sizeof(uint8_t), this->blockSize);
    } else if (this->bitsPerSample == 16){
        fprintf(stderr, "%d\n", fr->read_file(data, sizeof(uint16_t), this->blockSize));
    } else if (this->bitsPerSample == 24){
        fr->read_file(data, 3, this->blockSize);
    }
    return 1;
}

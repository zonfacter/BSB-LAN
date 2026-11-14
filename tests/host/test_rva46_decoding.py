"""Exercise the production scalar readers with observed Eurocontrol M payloads."""
import unittest

from source_harness import ROOT, between, compile_and_run


class Rva46DecodingRegression(unittest.TestCase):
    def test_legacy_configuration_and_operating_level_enums(self):
        source = (ROOT / "BSB_LAN/include/print_telegram.h").read_text(encoding="utf-8")
        enum_reader = "void printENUM(" + between(source, "void printENUM(", "uint16_t printKat(")
        decoder = "case VT_RVA_SETTING:" + between(source, "case VT_RVA_SETTING:", "case VT_WEEKDAY:")
        language = (ROOT / "BSB_LAN/localization/LANG_EN.h").as_posix()
        header = (ROOT / "BSB_LAN/include/legacy_rva.h").as_posix()
        compile_and_run(r'''
#include <stdio.h>
#include "''' + language + r'''"
#include "''' + header + r'''"
typedef uint8_t byte;
typedef const char *uint_farptr_t;
#define pgm_read_byte_far(p) (*reinterpret_cast<const unsigned char *>(p))
enum { VT_RVA_SETTING, VT_RVA_LEVEL };
struct Bus { int getPl_start() const { return 13; } } instance, *bus=&instance;
struct Decoded { int type; const char *enumstr; uint16_t enumstr_len;
                 const char *enumdescaddr; char value[32]; int error; } decodedTelegram;
static void printToDebug(const char *) {}
static void printFmtToDebug(const char *, ...) {}
static void undefinedValueToBuffer(char *out) { strcpy(out,"---"); }
''' + enum_reader + r'''
static void read(byte *msg, int data_len, int type, const char *labels, uint16_t length) {
  decodedTelegram={type,labels,length,nullptr,{},0};
  switch (type) { ''' + decoder + r''' }
}
#define CHECK(c) do { if(!(c)) { fprintf(stderr,"line %d: %s\n",__LINE__,#c);return 1;} } while(0)
int main() {
  byte frame[40]={};
  frame[14]=0xFF;
  read(frame,2,VT_RVA_SETTING,RVA_DHW_REQUEST_ENUM,sizeof(RVA_DHW_REQUEST_ENUM));
  CHECK(strcmp(decodedTelegram.value,"255")==0 && strcmp(decodedTelegram.enumdescaddr,RVA_DHW_THERMOSTAT_TEXT)==0);
  frame[14]=0;
  read(frame,2,VT_RVA_SETTING,RVA_DHW_REQUEST_ENUM,sizeof(RVA_DHW_REQUEST_ENUM));
  CHECK(strcmp(decodedTelegram.enumdescaddr,RVA_DHW_SENSOR_TEXT)==0);
  read(frame,2,VT_RVA_SETTING,RVA_BURNER_CONFIG_ENUM,sizeof(RVA_BURNER_CONFIG_ENUM));
  CHECK(strcmp(decodedTelegram.enumdescaddr,RVA_BURNER_SINGLE_TEXT)==0);
  frame[14]=0xFF;
  read(frame,2,VT_RVA_SETTING,RVA_BURNER_CONFIG_ENUM,sizeof(RVA_BURNER_CONFIG_ENUM));
  CHECK(strcmp(decodedTelegram.enumdescaddr,RVA_BURNER_TWO_TEXT)==0);
  frame[13]=1;
  read(frame,2,VT_RVA_SETTING,RVA_BURNER_CONFIG_ENUM,sizeof(RVA_BURNER_CONFIG_ENUM));
  CHECK(strcmp(decodedTelegram.value,"---")==0 && !decodedTelegram.enumdescaddr);
  frame[13]=0;frame[14]=1;
  read(frame,2,VT_RVA_SETTING,RVA_BURNER_CONFIG_ENUM,sizeof(RVA_BURNER_CONFIG_ENUM));
  CHECK(decodedTelegram.error==258 && strcmp(decodedTelegram.value,"1")==0);
  const char *levels[]={RVA_LEVEL_FROST_TEXT,RVA_LEVEL_REDUCED_TEXT,RVA_LEVEL_COMFORT_TEXT};
  for (byte level=0;level<3;level++) {
    frame[13]=level;frame[14]=1;
    read(frame,2,VT_RVA_LEVEL,RVA_M_LEVEL_ENUM,sizeof(RVA_M_LEVEL_ENUM));
    CHECK(!decodedTelegram.error && strcmp(decodedTelegram.enumdescaddr,levels[level])==0);
    CHECK(frame[13]==level && frame[14]==1);
  }
  frame[13]=9;
  read(frame,2,VT_RVA_LEVEL,RVA_M_LEVEL_ENUM,sizeof(RVA_M_LEVEL_ENUM));
  CHECK(decodedTelegram.error==258 && strcmp(decodedTelegram.value,"9")==0);
  read(frame,1,VT_RVA_LEVEL,RVA_M_LEVEL_ENUM,sizeof(RVA_M_LEVEL_ENUM));
  CHECK(decodedTelegram.error==256 && strcmp(decodedTelegram.value,"---")==0);
  return 0;
}
''')

    def test_recorded_scalars_disabled_room_sensor_and_independent_relays(self):
        source = (ROOT / "BSB_LAN/include/print_telegram.h").read_text(encoding="utf-8")
        numeric = "int _printFIXPOINT(" + between(source, "int _printFIXPOINT(", "void printFIXPOINT_BYTE(")
        unsigned = "void printFIXPOINT_BYTE_US(" + between(source, "void printFIXPOINT_BYTE_US(", "void printENUM(")
        byte_reader = "void printBYTE(" + between(source, "void printBYTE(", "void printWORD(")
        choice = "void printCHOICE(" + between(source, "void printCHOICE(", "void printCustomENUM(")
        language = (ROOT / "BSB_LAN/localization/LANG_EN.h").as_posix()
        header = (ROOT / "BSB_LAN/include/legacy_rva.h").as_posix()
        compile_and_run(r'''
#include <stdio.h>
#include <string>
#include "''' + language + r'''"
#include "''' + header + r'''"
typedef uint8_t byte;
typedef const char *uint_farptr_t;
#define BUS_PPS 2
#define FL_SPECIAL_INF 16
struct Bus { int getPl_start() const { return 13; } int getBusType() const { return 1; } } instance,*bus=&instance;
struct Decoded { uint32_t flags; char value[64]; const char *unit; int error; } decodedTelegram={};
static void printToDebug(const char *) {}
static void printFmtToDebug(const char *,...) {}
static void printDebugValueAndUnit(const char *,const char *) {}
static void prepareToPrintHumanReadableTelegram(byte *,byte,int) {}
static void undefinedValueToBuffer(char *out) { strcpy(out,"---"); }
static void printENUM(const char *,uint16_t,uint16_t value,int) {
  snprintf(decodedTelegram.value,sizeof(decodedTelegram.value),"%u",value);
}
''' + numeric + unsigned + byte_reader + choice + r'''
#define CHECK(c) do { if(!(c)) { fprintf(stderr,"line %d: %s\n",__LINE__,#c);return 1;} } while(0)
int main() {
  byte frame[40]={};
  frame[14]=7;frame[15]=9; // 00 07 09: measured flow, 1801 / 64
  const std::string original(reinterpret_cast<char*>(frame),sizeof(frame));
  printFIXPOINT(frame,3,64,1); CHECK(std::string(decodedTelegram.value)=="28.1");
  CHECK(std::string(reinterpret_cast<char*>(frame),sizeof(frame))==original);
  frame[14]=7;frame[15]=0x80;
  printFIXPOINT(frame,3,64,1); CHECK(std::string(decodedTelegram.value)=="30.0");
  frame[14]=5;frame[15]=0xC0;
  printFIXPOINT(frame,3,64,1); CHECK(std::string(decodedTelegram.value)=="23.0");
  frame[14]=0xFF;frame[15]=0xC0;
  printFIXPOINT(frame,3,64,1); CHECK(std::string(decodedTelegram.value)=="-1.0");
  frame[13]=1;frame[14]=0;frame[15]=0; // actual room sensor is invalid, not zero degrees
  printFIXPOINT(frame,3,64,1); CHECK(std::string(decodedTelegram.value)=="---");
  decodedTelegram.error=0;
  printFIXPOINT(frame,2,64,1); CHECK(decodedTelegram.error==256);

  decodedTelegram={};frame[13]=0;frame[14]=0x1C;
  printFIXPOINT_BYTE_US(frame,2,2,1); CHECK(std::string(decodedTelegram.value)=="14.0");
  frame[14]=6;
  printBYTE(frame,2); CHECK(std::string(decodedTelegram.value)=="6"); // minutes, no conversion to seconds
  frame[14]=0xFF;
  printCHOICE(frame,2,nullptr,0); CHECK(std::string(decodedTelegram.value)=="1");
  frame[13]=1;
  printCHOICE(frame,2,nullptr,0); CHECK(std::string(decodedTelegram.value)=="---");

  uint8_t block[8]={0,0,0xFF,0,0,0,0,0}, value=0;
  CHECK(decodeRawRelayOnOff(block,8,(2u<<16)|(1u<<20),value) && value==1);
  CHECK(decodeRawRelayOnOff(block,8,(0u<<16)|(1u<<20),value) && value==0);
  CHECK(decodeRawRelayOnOff(block,8,(1u<<16)|(1u<<20),value) && value==0);
  block[0]=0xFF; // synthetic open direction; independent of pump and close contact
  CHECK(decodeRawRelayOnOff(block,8,(0u<<16)|(1u<<20),value) && value==1);
  CHECK(decodeRawRelayOnOff(block,8,(1u<<16)|(1u<<20),value) && value==0);
  block[0]=0;block[1]=0xFF; // synthetic close direction, not a live observation
  CHECK(decodeRawRelayOnOff(block,8,(0u<<16)|(1u<<20),value) && value==0);
  CHECK(decodeRawRelayOnOff(block,8,(1u<<16)|(1u<<20),value) && value==1);
  return 0;
}
''')


if __name__ == "__main__":
    unittest.main()

//transmitor
// FINAL DRAFT - 4:56

#include <asf.h>
#include <string.h>
#include "config.h"
#include "phy.h"
#include "nwk.h"
#include "sys.h"
#include "sysTimer.h"
#include "at30tse75x.h"

uint16_t light2;
uint16_t temp;

typedef struct{
	 uint32_t startDelimeter;
	 uint16_t length;
	 uint16_t sequenceNumber;
	 uint16_t temperature;
	 uint16_t light;
	 char message[16];
	 uint16_t crc;
	 uint32_t endDelimeter;
} message_t;  

static void appInit(void);
static void timerHandler(SYS_Timer_t *timer);
static void sendData(void);
static void sendDataConf(NWK_DataReq_t* request);
static void calculateCRC(uint8_t* data, uint8_t lenght, uint16_t* storage);

static SYS_Timer_t txTimer;
static bool radioBusy = false;
static message_t payload;
static NWK_DataReq_t txRequest;

typedef struct adc_dev_inst adc_dev_inst_t;
typedef struct adc_config adc_config_t;
typedef struct adc_seq_config adc_seq_config_t;
typedef struct adc_ch_config adc_ch_config_t;

void configure_adc(void);
void start_timer(void);
void adc_conversion_complete(void);

// the device instance for AD0
static adc_dev_inst_t adc0;
static uint16_t conversion_result = 0xff;
static bool conversion_complete = true;


static void appInit(void){
	NWK_SetAddr(APP_ADDR);
	NWK_SetPanId(APP_PANID);
	PHY_SetChannel(APP_CHANNEL);
	PHY_SetRxState(false);
	
	// initialize timer => sample + send once per sec
	txTimer.interval = 1000;
	txTimer.mode=SYS_TIMER_PERIODIC_MODE;
	txTimer.handler = timerHandler;
	SYS_TimerStart(&txTimer);
}

static void timerHandler(SYS_Timer_t *timer){
	double temperature;
	at30tse_read_temperature(&temperature);

	temp = temperature;
	// printf("Temp : %d\r\n", temp);
			
	//LIGHT SENSOR VALUES
	if(conversion_complete) {
		
		light2 = conversion_result;
		// printf("Light = %d\r\n", light2);

		} else {
		printf("busy\r\n");

	}
	if (timer == &txTimer){
		if (!radioBusy){
			sendData();
		}
	}
}


static void calculateCRC(uint8_t* data, uint8_t lenght, uint16_t* storage){
	
	uint16_t result =0;
	uint8_t index;
	for(index = 0; index <lenght; index ++){
		result += data[index] * (index + 1);
	}
	
	*storage = result;
}


static void sendData(void){
	static uint16_t sequenceNumber =1;

	//create fake data
	payload.startDelimeter = 0xAABBCCDD;
	payload.length = 22;
	payload.sequenceNumber = sequenceNumber ++;
	payload.temperature = temp;
	payload.light = light2;
	strcpy(payload.message, "Room_1");
	payload.crc = 0;
	calculateCRC((uint8_t*) &payload.sequenceNumber, payload.length, &payload.crc);
	payload.endDelimeter = 0xDDCCBBAA;
	
	txRequest.dstAddr = 1;
	txRequest.dstEndpoint = APP_ENDPOINT;
	txRequest.srcEndpoint= APP_ENDPOINT;
	txRequest.options = 0;
	txRequest.data= (uint8_t*) &payload;
	txRequest.size = sizeof(payload);
	txRequest.confirm= sendDataConf;  
	
	NWK_DataReq(&txRequest);
	radioBusy = true;
}

static void sendDataConf(NWK_DataReq_t* request){
	if(request == &txRequest){
		radioBusy = false;
		if(request->status==NWK_SUCCESS_STATUS){
		ioport_toggle_pin_level(LED0);
		}
	}
}
//======================================= Start of Sensor Code================================//


void adc_conversion_complete(void) {
	
	// store result in our global variable
	conversion_result = adc_get_last_conv_value(&adc0);
	conversion_complete = true;
	adc_clear_status(&adc0, ADCIFE_SCR_SEOC);
	
	adc_start_software_conversion(&adc0);
	
}

void configure_adc(void) {
	adc_config_t adcConfig = {
		.clksel = ADC_CLKSEL_APBCLK,		// drive the ADC from the bus clock
		.prescal = ADC_PRESCAL_DIV512,		// prescaler of 512 (slowest sample and hold)
		.speed = ADC_SPEED_75K,				// slowest sampling speed (for current consumption)
		.refsel = ADC_REFSEL_0,				// internal 1.0V Vref
		.start_up = CONFIG_ADC_STARTUP		// startup penalty (in clock cycles)
	};
	
	adc_seq_config_t adcSequencerConfig = {
		.bipolar = ADC_BIPOLAR_SINGLEENDED,	// single-ended input
		.res = ADC_RES_12_BIT,				// 12-bit resolution
		.zoomrange = ADC_ZOOMRANGE_0,		// no zooming; (interesting feature!)
		.muxpos = ADC_MUXPOS_2,				// AD0
		.muxneg = ADC_MUXNEG_1,				// ground reference from pad
		.internal = ADC_INTERNAL_2,			// (implied by MUXPOS_0 and MUXNEG_1)
		.gcomp = ADC_GCOMP_DIS,				// no gain compensation
		.hwla = ADC_HWLA_DIS				// no left alignment
	};
	
	struct adc_ch_config adcChannelConfig = {
		.seq_cfg = &adcSequencerConfig,		// sequencer configuration
		.internal_timer_max_count = 0,		// timer not used
		.window_mode = ADC_WM_OFF,			// no windowing
		.low_threshold = 0,					// no low threshold
		.high_threshold = 0,				// no high threshold
	};
	
	adc_init(&adc0, ADCIFE, &adcConfig);
	adc_enable(&adc0);
	adc_ch_set_config(&adc0, &adcChannelConfig);
	adc_set_callback(&adc0, ADC_SEQ_SEOC, adc_conversion_complete, ADCIFE_IRQn, 1);
}

//======================================= End of Sensor Code==================================//
int main (void)
{
	sysclk_init();	
	board_init();
	SYS_Init();
	appInit();
	configure_adc();
	adc_conversion_complete();
	
	usart_serial_options_t serial_config = {
		.baudrate = 9600,
		.charlength = US_MR_CHRL_8_BIT,
		.paritytype = US_MR_PAR_NO,
		.stopbits = US_MR_NBSTOP_1
	};
	usart_serial_init(USART1, &serial_config);
	
	// setup stdio
	stdio_base = USART1;
	ptr_put = (int(*)(void volatile*, char)) usart_serial_putchar;
	setbuf(stdout, NULL);
	
	at30tse_init();
	at30tse_write_config_register(AT30TSE_CONFIG_RES(AT30TSE_CONFIG_RES_12_bit));
	while (1) {
		
		SYS_TaskHandler();
	
	}
}

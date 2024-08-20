import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.SPI as SPI

# Instruction table
Eeprom_Read = 0x03
Eeprom_Write = 0x02
Eeprom_Wrdi = 0x04
Eeprom_Wren = 0x06
Eeprom_Rdsr = 0x05
Eeprom_Wrsr = 0x01

class EEPROM25XX:
    def __init__(self, bus=2, device=0, cs_pin="P9_42", spi_speed_hz=4000000):
        self.cs_pin = cs_pin
        GPIO.setup(self.cs_pin, GPIO.OUT)
        # Setup SPI
        self.spi = SPI.SPI(bus, device)
        self.spi.msh = spi_speed_hz
        self.spi.mode = 0
    
    def eeprom_read_data(self, address, length):
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.xfer2([Eeprom_Read, (address >> 8) & 0xFF, address & 0xFF])
        data = self.spi.readbytes(length)
        GPIO.output(self.cs_pin, GPIO.HIGH)
        return data

    def eeprom_write(self, address, data):
        # Enable writing
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.xfer2([Eeprom_Wren])
        GPIO.output(self.cs_pin, GPIO.HIGH)

        # Write data
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.xfer2([Eeprom_Write, (address >> 8) & 0xFF, address & 0xFF] + data)
        GPIO.output(self.cs_pin, GPIO.HIGH)

        # Wait for the write to complete
        while True:
            GPIO.output(self.cs_pin, GPIO.LOW)
            status = self.spi.xfer2([Eeprom_Rdsr, 0])[1]
            
            GPIO.output(self.cs_pin, GPIO.HIGH)
            if not (status & 0x01):  # Check the WIP (Write-In-Progress) bit
                break
            time.sleep(0.001)

if __name__ == "__main__":
    eeprom = EEPROM25XX()
    eeprom.eeprom_write(0x0000, [0x3B])  # Write 0xAA to address 0x0000
    data = eeprom.eeprom_read_data(0x0000, 1)  # Read byte from address 0x0000
    print("Data read from EEPROM: ",hex(data[0]))

EESchema Schematic File Version 4
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L 39-53-2224:39-53-2224 J1
U 1 1 5C449C40
P 1900 1750
F 0 "J1" H 2350 2015 50  0000 C CNN
F 1 "39-53-2224" H 2350 1924 50  0000 C CNN
F 2 "39532224" H 2650 1850 50  0001 L CNN
F 3 "https://componentsearchengine.com/Datasheets/1/39-53-2224.pdf" H 2650 1750 50  0001 L CNN
F 4 "Molex FFC/FPC THROUGH HOLE Series 1.25mm Pitch 22 Way 1 Row Right Angle Through Hole Female FPC Connector" H 2650 1650 50  0001 L CNN "Description"
F 5 "5.4" H 2650 1550 50  0001 L CNN "Height"
F 6 "Molex" H 2650 1450 50  0001 L CNN "Manufacturer_Name"
F 7 "39-53-2224" H 2650 1350 50  0001 L CNN "Manufacturer_Part_Number"
F 8 "6704345" H 2650 1250 50  0001 L CNN "RS Part Number"
F 9 "http://uk.rs-online.com/web/p/products/6704345" H 2650 1150 50  0001 L CNN "RS Price/Stock"
F 10 "538-39-53-2224" H 2650 1050 50  0001 L CNN "Mouser Part Number"
F 11 "https://www.mouser.com/Search/Refine.aspx?Keyword=538-39-53-2224" H 2650 950 50  0001 L CNN "Mouser Price/Stock"
	1    1900 1750
	1    0    0    -1  
$EndComp
$Comp
L Device:R R1
U 1 1 5C449FDA
P 3250 2000
F 0 "R1" H 3320 2046 50  0000 L CNN
F 1 "R" H 3320 1955 50  0000 L CNN
F 2 "" V 3180 2000 50  0001 C CNN
F 3 "~" H 3250 2000 50  0001 C CNN
	1    3250 2000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R2
U 1 1 5C44A0A2
P 3700 2100
F 0 "R2" H 3770 2146 50  0000 L CNN
F 1 "R" H 3770 2055 50  0000 L CNN
F 2 "" V 3630 2100 50  0001 C CNN
F 3 "~" H 3700 2100 50  0001 C CNN
	1    3700 2100
	1    0    0    -1  
$EndComp
Wire Wire Line
	2800 1750 3250 1750
Wire Wire Line
	3250 1750 3250 1850
Wire Wire Line
	3250 2150 3250 2250
Wire Wire Line
	3250 2250 2800 2250
$EndSCHEMATC

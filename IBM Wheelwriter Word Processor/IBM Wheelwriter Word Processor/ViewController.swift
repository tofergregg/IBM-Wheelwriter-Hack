//
//  ViewController.swift
//  IBM Wheelwriter Word Processor
//
//  Created by Chris Gregg on 2/2/17.
//  Copyright © 2017 Chris Gregg. All rights reserved.
//

import Cocoa
import ORSSerial

class ViewController: NSViewController, ORSSerialPortDelegate {
    // class variables for sending data
    var printData : Data!
    var header : Data!
    var serialPort: ORSSerialPort?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Do any additional setup after loading the view.
    }
    
    override var representedObject: Any? {
        didSet {
            // Update the view, if already loaded.
        }
    }
    
    @IBOutlet var fullTextView: NSTextView!
    
    @IBAction func bold(sender : Any) {
        print("User pressed bold");
        let fm = NSFontManager.shared()
        let fakeBoldButton = NSButton()
        fakeBoldButton.tag = 2 // tag of 2 tells the fontmanager we want to change bold
        
        let fontName = fm.selectedFont?.fontName ?? "None"
        print(fontName)
        if (fontName.contains("Bold")) {
            fm.removeFontTrait(fakeBoldButton)
        } else {
            fm.addFontTrait(fakeBoldButton)
        }
    }
    
    @IBAction func printDoc(sender: Any) {
        let attribText = fullTextView.attributedString()
        let plainText = fullTextView.string ?? ""
        
        // find underlined and bolded text
        
        var charCount = 0
        var printable = CharacterSet.letters
        printable.formUnion(CharacterSet.decimalDigits)
        printable.formUnion(CharacterSet.whitespacesAndNewlines)
        printable.formUnion(CharacterSet.punctuationCharacters)
        
        var bolded_attr : Bool
        var underlined_attr : Bool
        
        // current state
        var bolded = false;
        var underlined = false;
        
        // typewriter_string
        var typewriterString = ""
        
        for char in plainText.characters {
            if (!printable.contains(UnicodeScalar("\(char)")!)) {
                continue // skip non-printable characters
            }
            var rng = NSRange()
            
            let fontAttribName : NSFont? = attribText.attribute(NSFontAttributeName, at: charCount, effectiveRange: &rng) as! NSFont?
            if (fontAttribName != nil) {
                bolded_attr = (fontAttribName?.fontName.contains("Bold"))!
            } else {
                bolded_attr = false
            }
            
            underlined_attr = !(attribText.attribute(NSUnderlineStyleAttributeName, at: charCount, effectiveRange: &rng) == nil)
            
            print(char, terminator: ", underlined: ")
            print(underlined_attr, terminator: ", bold: ")
            print(bolded_attr)
            
            if (bolded_attr) {
                if (!bolded) {
                    bolded = true
                    typewriterString += "\(Character(UnicodeScalar(2)))" // bold control character for typewriter
                }
            } else {
                if (bolded) {
                    bolded = false;
                    typewriterString += "\(Character(UnicodeScalar(2)))"
                }
            }
            
            if (underlined_attr) {
                if (!underlined) {
                    underlined = true
                    typewriterString += "\(Character(UnicodeScalar(3)))" // underline control character
                }
            } else {
                if (underlined) {
                    underlined = false;
                    typewriterString += "\(Character(UnicodeScalar(3)))"
                }
            }
            typewriterString += "\(char)"
            charCount+=1
        }
        typewriterString += "\n" // just to be sure we end with a newline
        
        print(typewriterString)
        do {
            try sendToIBM(typewriterText: typewriterString)
        }
        catch {
            print("Too much data (limit: 64KB)")
        }
    }
    
    func sendToIBM(typewriterText : String) throws {
        
        // max size, 64KB
        if (typewriterText.characters.count > (1 << 16)) {
            throw NSError(domain: "Cannot send more than 64KB to device.", code: -1, userInfo: nil)
        }
        
        // convert string to data
        printData = typewriterText.data(using: .utf8)! as Data
        
        // set up header to tell typewriter we are printing a bunch of text
        // first, convert the size of the text into two bytes
        // as binary: 0000 0001 1010 0101 (421)
        
        let textLength = typewriterText.characters.count
        let lowByte = UInt8(textLength & 0xff)
        let highByte = UInt8(textLength >> 8)
        
        header = Data(bytes: [0x0, lowByte, highByte])
        
        
        self.serialPort = ORSSerialPort(path: "/dev/tty.wchusbserial1410")
        serialPort?.baudRate = 115200
        self.serialPort?.delegate = self
        serialPort?.open()
    }
    
    func sendDataToArduino() {
        let MAX_DATA = 40 // only 40 characters at once so the arudino buffer doesn't overflow
        if (printData.count > 0) {
            let endIndex = min(MAX_DATA,printData.endIndex)
            
            let textToSend = printData.subdata(in: 0..<endIndex)
            printData = printData.subdata(in: endIndex..<printData.endIndex)
            serialPort?.send(textToSend)
        } else {
            serialPort?.close()
        }
    }
    
    // ORSSerialDelegate methods
    func serialPort(_ serialPort: ORSSerialPort, didReceive data: Data) {
        if let string = NSString(data: data as Data, encoding: String.Encoding.utf8.rawValue) {
            print("\(string)")
            if (string.contains("\n")) {
                sendDataToArduino()
            }
        }
    }
    
    func serialPort(_ serialPort: ORSSerialPort, didEncounterError error: Error) {
        print("Serial port (\(serialPort)) encountered error: \(error)")
    }
    
    func serialPortWasOpened(_ serialPort: ORSSerialPort) {
        print("Serial port \(serialPort) was opened")
        // delay a bit more before sending data, so that the
        // Arduino can start the sketch (it gets reset every time
        // the serial port is opened...)
        let delayInSeconds = 1.5
        DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + delayInSeconds) {
            serialPort.send(self.header)
            self.sendDataToArduino()
        }
    }
    
    /**
     *  Called when a serial port is removed from the system, e.g. the user unplugs
     *  the USB to serial adapter for the port.
     *
     *	In this method, you should discard any strong references you have maintained for the
     *  passed in `serialPort` object. The behavior of `ORSSerialPort` instances whose underlying
     *  serial port has been removed from the system is undefined.
     *
     *  @param serialPort The `ORSSerialPort` instance representing the port that was removed.
     */
    public func serialPortWasRemoved(fromSystem serialPort: ORSSerialPort) {
        self.serialPort = nil
    }
}


//
//  ViewController.swift
//  IBM Wheelwriter Word Processor
//
//  Created by Chris Gregg on 2/2/17.
//  Copyright © 2017 Chris Gregg. All rights reserved.
//

import Cocoa
import ORSSerial

// implement resize function
// source (slightly modified): http://stackoverflow.com/a/30422317/561677
extension NSImage {
    func resizeImage(width: CGFloat, _ height: CGFloat) -> NSImage {
        let img = NSImage(size: CGSize(width:width, height:height))
        
        img.lockFocus()
        let ctx = NSGraphicsContext.current()
        ctx?.imageInterpolation = .high
        self.draw(in: NSMakeRect(0, 0, width, height), from: NSMakeRect(0, 0, size.width, size.height), operation: .copy, fraction: 1)
        img.unlockFocus()
        
        return img
    }
}

struct ImageAndPosition {
    var location : Int;
    var data : Data
    
    init(location: Int, data: Data) {
        self.location = location
        self.data = data
    }
}

class ViewController: NSViewController, ORSSerialPortDelegate {
    // class variables for sending data
    var printData : Data!
    var header : Data!
    var runData : [[UInt8]]!
    
    var serialPort: ORSSerialPort?
    
    var sendingText = false
    var sendingImage = false
    
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
        // handle embedded images
        let attribText = fullTextView.attributedString()

        print(attribText)
        
        var imageArray : [ImageAndPosition] = []
        
        if (attribText.containsAttachments) {
            // keep track of all the attachments as data for later printing
            attribText.enumerateAttribute(NSAttachmentAttributeName, in: NSMakeRange(0,attribText.length), options: NSAttributedString.EnumerationOptions(rawValue: 0), using: {(value, range, stop) in
                if let attachment: Any = value   {
                    if let attachment = attachment as? NSTextAttachment,
                        let fileWrapper = attachment.fileWrapper,
                        let data = fileWrapper.regularFileContents {
                        print("\(range.location),\(range.length)")
                        imageArray.append(ImageAndPosition(location: range.location, data: data))
                        //printImageToTypewriter(data: data)
                    }
                }
            })
        }
        
        let typewriterString = parseTextFromView()

        print(typewriterString)
        do {
            try sendTextToIBM(typewriterText: typewriterString)
        }
        catch {
            print("Too much data (limit: 64KB)")
        }
    }
    
    func sendNextPartToTypewriter() {
        //
    }
    
    func printImageToTypewriter(data: Data) {
        let maxDimension : CGFloat = 50
        
        let img = NSImage(data:data)?.resizeImage(width: maxDimension, maxDimension)

        print (img ?? "<no image>")
        let raw_img : NSBitmapImageRep! = NSBitmapImageRep(data: (img?.tiffRepresentation)!)
        
        let height = raw_img.pixelsHigh
        let width = raw_img.pixelsWide
        
        // the following was borrowed from: https://gist.github.com/bpercevic/b5b193c3379b3f048210
        var bitmapData: UnsafeMutablePointer<UInt8> = raw_img.bitmapData!
        var r, g, b: UInt8
        
        // convert all pixels to black & white
        var bw_pixels : [UInt8] = []
        for _ in 0 ..< height { // rows
            for _ in 0 ..< width { // cols
                r = bitmapData.pointee
                bitmapData = bitmapData.advanced(by: 1)
                g = bitmapData.pointee
                bitmapData = bitmapData.advanced(by: 1)
                b = bitmapData.pointee
                bitmapData = bitmapData.advanced(by: 2) // ignore alpha
                
                // a = bitmapData.pointee
                //bitmapData = bitmapData.advanced(by: 1)
                
                // from here: http://stackoverflow.com/a/14331/561677
                let grayscalePixel = (0.2125 * Double(r)) + (0.7154 * Double(g)) + (0.0721 * Double(b))
                
                // convert to b&w:
                // from here: http://stackoverflow.com/a/18778280/561677
                let finalPixel : UInt8
                if (grayscalePixel < 128) {
                    finalPixel = 0
                } else {
                    finalPixel = 255
                }
                bw_pixels.append(finalPixel)
                //print("\(grayscalePixel),\(finalPixel)")
            }
        }
        
        // determine runs for printing
        var runs : [[UInt8]] = [[1]] // initial command to print an image is 1
        
        for row in 0 ..< height { // rows
            var prevBit = bw_pixels[row * width] // start at the first bit on the row
            var bitCount = 0
            var lineBits = 0
            for col in 0 ..< width { // cols
                let currentBit = bw_pixels[row * width + col]
                if currentBit != prevBit {
                    if prevBit == 0 {
                        runs.append([UInt8(bitCount & 0xff), UInt8(bitCount >> 8), 46])
                    } else {
                        runs.append([UInt8(bitCount & 0xff), UInt8(bitCount >> 8), 32])
                    }
                    lineBits += bitCount
                    bitCount = 0
                    prevBit = currentBit
                }
                bitCount += 1
            }
            if prevBit == 0 { // 0 is black
                // don't bother printing a string of spaces at the end, just dots
                runs.append([UInt8(bitCount & 0xff), UInt8(bitCount >> 8), 46])
                lineBits += bitCount
            }
            runs.append([UInt8(lineBits & 0xff), UInt8(lineBits >> 8), 10])
        }
        runs.append([0, 0, 0]) // end of image
        runData = runs
        print(runData)
        sendImageToIBM(runs: runs)
    }
    
    func processImage(runs : [[UInt8]]) {
        for run in runs {
            if run == [1,0,0] || run == [0, 0, 0] {
                continue; // skip first and last
            }
            let runLength = Int(run[0]) + (Int(run[1]) << 8)
            if (run[2] == 10) {
                // just print a newline
                print()
            } else {
                for _ in 0..<runLength {
                    print(Character(UnicodeScalar(run[2])), terminator:"")
                }
            }
        }
    }
    
    func parseTextFromView() -> String {
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
        return typewriterString
    }
    func sendTextToIBM(typewriterText : String) throws {
        
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
        sendingText = true
        serialPort?.open()
    }
    
    func sendImageToIBM(runs : [[UInt8]]) {
        self.serialPort = ORSSerialPort(path: "/dev/tty.wchusbserial1410")
        serialPort?.baudRate = 115200
        self.serialPort?.delegate = self
        sendingImage = true
        serialPort?.open()

    }
    
    func sendTextToArduino() {
        let MAX_DATA = 40 // only 40 characters at once so the arudino buffer doesn't overflow
        if (printData.count > 0) {
            let endIndex = min(MAX_DATA,printData.endIndex)
            
            let textToSend = printData.subdata(in: 0..<endIndex)
            printData = printData.subdata(in: endIndex..<printData.endIndex)
            serialPort?.send(textToSend)
        } else {
            serialPort?.close()
            sendingText = false
            sendNextPartToTypewriter()
        }
    }
    
    func sendImageToArduino() {
        let MAX_DATA = 20 // 3 * 3 bytes = 60 at a time
        if (runData.count > 0) {
            let endIndex = min(MAX_DATA, runData.endIndex)
            let runDataToSend = runData[0..<endIndex]
            let newRunData = runData[endIndex..<runData.endIndex]
            // manually copy newRunData into runData, because it is just an ArraySlice now
            runData = []
            for d in newRunData {
                runData.append(d)
            }
            // create an actual data to send
            var dataToSend : Data = Data()
            for d in runDataToSend {
                dataToSend.append(d[0])
                if (d.count > 1) { // the first element is a single value
                    dataToSend.append(d[1])
                    dataToSend.append(d[2])
                }
            }
            //for d in dataToSend {
            //    print (d)
            //}
            serialPort?.send(dataToSend)
        } else {
            serialPort?.close()
            sendingImage = false
            sendNextPartToTypewriter()
        }
    }
    
    @IBAction func setupMargins(sender: NSButton) {
        print("setting up...")
    }
    
    // ORSSerialDelegate methods
    func serialPort(_ serialPort: ORSSerialPort, didReceive data: Data) {
        if let string = NSString(data: data as Data, encoding: String.Encoding.utf8.rawValue) {
            print("\(string)")
            if (string.contains("\n")) {
                if sendingText {
                    sendTextToArduino()
                } else if sendingImage {
                    sendImageToArduino()
                }
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
            //serialPort.send(Data(bytes: [0x04])) // reset typewriter
            if self.sendingText {
                serialPort.send(self.header)
                self.sendTextToArduino()
            } else if (self.sendingImage) {
                self.sendImageToArduino()
            }
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


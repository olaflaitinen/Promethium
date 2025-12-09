package io.promethium.io

import breeze.linalg._
import io.promethium.core.{SeismicDataset, IoException}
import scala.util.{Try, Success, Failure}

/**
 * SEG-Y format I/O for seismic data.
 *
 * Note: This is a stub implementation. For production use,
 * integrate with a full SEG-Y library such as javaseis or
 * implement complete binary format parsing.
 */
object SegyIO {
  
  /**
   * Read seismic data from SEG-Y file.
   *
   * @param path Path to SEG-Y file
   * @return SeismicDataset
   * @throws IoException if file cannot be read
   */
  def read(path: String): SeismicDataset = {
    import java.io.{File, RandomAccessFile}
    import java.nio.{ByteBuffer, ByteOrder}
    
    val file = new File(path)
    if (!file.exists()) {
      throw IoException(s"File not found: $path")
    }
    
    Try {
      val raf = new RandomAccessFile(file, "r")
      try {
        // Read textual header (3200 bytes) - skip for now
        raf.seek(3200)
        
        // Read binary header (400 bytes)
        val binaryHeader = new Array[Byte](400)
        raf.read(binaryHeader)
        val bb = ByteBuffer.wrap(binaryHeader).order(ByteOrder.BIG_ENDIAN)
        
        // Sample interval in microseconds (bytes 17-18)
        bb.position(16)
        val dtMicros = bb.getShort().toInt & 0xFFFF
        val dt = dtMicros / 1000000.0  // Convert to seconds
        
        // Samples per trace (bytes 21-22)
        bb.position(20)
        val nSamples = bb.getShort().toInt & 0xFFFF
        
        // Format code (bytes 25-26)
        bb.position(24)
        val formatCode = bb.getShort()
        
        // Calculate number of traces
        val dataStart = 3600L  // After headers
        val traceHeaderSize = 240
        val bytesPerSample = formatCode match {
          case 1 => 4  // IBM float
          case 2 => 4  // 4-byte int
          case 3 => 2  // 2-byte int
          case 5 => 4  // IEEE float
          case _ => 4  // Default to 4
        }
        val traceSize = traceHeaderSize + nSamples * bytesPerSample
        val nTraces = ((file.length() - dataStart) / traceSize).toInt
        
        // Read traces
        val traces = DenseMatrix.zeros[Double](nTraces, nSamples)
        raf.seek(dataStart)
        
        for (i <- 0 until nTraces) {
          // Skip trace header
          raf.skipBytes(traceHeaderSize)
          
          // Read samples
          val sampleBytes = new Array[Byte](nSamples * bytesPerSample)
          raf.read(sampleBytes)
          val sampleBB = ByteBuffer.wrap(sampleBytes).order(ByteOrder.BIG_ENDIAN)
          
          for (j <- 0 until nSamples) {
            val value = formatCode match {
              case 5 => sampleBB.getFloat().toDouble  // IEEE float
              case 1 => ibmToIeee(sampleBB.getInt())  // IBM float
              case _ => sampleBB.getFloat().toDouble
            }
            traces(i, j) = value
          }
        }
        
        SeismicDataset(
          traces = traces,
          dt = if (dt > 0) dt else 0.004,  // Default to 4ms if not set
          metadata = Map(
            "source" -> path,
            "format" -> "segy",
            "nTraces" -> nTraces.toString,
            "nSamples" -> nSamples.toString
          )
        )
      } finally {
        raf.close()
      }
    } match {
      case Success(dataset) => dataset
      case Failure(e) => throw IoException(s"Failed to read SEG-Y file: ${e.getMessage}")
    }
  }
  
  /**
   * Write seismic data to SEG-Y file.
   *
   * @param path    Output path
   * @param dataset Dataset to write
   */
  def write(path: String, dataset: SeismicDataset): Unit = {
    import java.io.{File, RandomAccessFile}
    import java.nio.{ByteBuffer, ByteOrder}
    
    Try {
      val raf = new RandomAccessFile(new File(path), "rw")
      try {
        // Write textual header (3200 bytes of spaces)
        val textHeader = new Array[Byte](3200)
        java.util.Arrays.fill(textHeader, ' '.toByte)
        raf.write(textHeader)
        
        // Write binary header (400 bytes)
        val binaryHeader = ByteBuffer.allocate(400).order(ByteOrder.BIG_ENDIAN)
        binaryHeader.position(16)
        binaryHeader.putShort((dataset.dt * 1000000).toInt.toShort)  // dt in microseconds
        binaryHeader.position(20)
        binaryHeader.putShort(dataset.nSamples.toShort)
        binaryHeader.position(24)
        binaryHeader.putShort(5.toShort)  // IEEE float format
        raf.write(binaryHeader.array())
        
        // Write traces
        for (i <- 0 until dataset.nTraces) {
          // Write trace header (240 bytes)
          val traceHeader = new Array[Byte](240)
          raf.write(traceHeader)
          
          // Write samples as IEEE floats
          val samples = ByteBuffer.allocate(dataset.nSamples * 4).order(ByteOrder.BIG_ENDIAN)
          for (j <- 0 until dataset.nSamples) {
            samples.putFloat(dataset.traces(i, j).toFloat)
          }
          raf.write(samples.array())
        }
      } finally {
        raf.close()
      }
    } match {
      case Success(_) => ()
      case Failure(e) => throw IoException(s"Failed to write SEG-Y file: ${e.getMessage}")
    }
  }
  
  /**
   * Convert IBM floating point to IEEE.
   */
  private def ibmToIeee(ibmFloat: Int): Double = {
    val sign = if ((ibmFloat & 0x80000000) != 0) -1.0 else 1.0
    val exponent = ((ibmFloat >> 24) & 0x7F) - 64
    val mantissa = (ibmFloat & 0x00FFFFFF).toDouble / 16777216.0
    sign * mantissa * math.pow(16.0, exponent)
  }
}

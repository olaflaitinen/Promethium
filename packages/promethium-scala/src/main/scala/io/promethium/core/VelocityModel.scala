package io.promethium.core

import breeze.linalg._
import breeze.numerics._

/**
 * 2D or 3D velocity model for seismic wave propagation.
 *
 * Velocity models are used for depth imaging, migration, and
 * physics-informed reconstruction algorithms.
 *
 * @param velocities 2D matrix of velocity values (m/s), indexed as (z, x)
 * @param dx         Horizontal grid spacing in meters
 * @param dz         Vertical grid spacing in meters
 * @param origin     Grid origin coordinates (x0, z0)
 * @param metadata   Key-value metadata pairs
 */
final case class VelocityModel(
  velocities: DenseMatrix[Double],
  dx: Double,
  dz: Double,
  origin: (Double, Double) = (0.0, 0.0),
  metadata: Map[String, String] = Map.empty
) {
  require(dx > 0, "Horizontal spacing dx must be positive")
  require(dz > 0, "Vertical spacing dz must be positive")
  require(velocities.rows > 0 && velocities.cols > 0, "Velocity grid must be non-empty")
  
  /** Number of horizontal grid points. */
  def nx: Int = velocities.cols
  
  /** Number of vertical grid points. */
  def nz: Int = velocities.rows
  
  /** Horizontal extent in meters. */
  def extentX: Double = (nx - 1) * dx
  
  /** Vertical extent in meters. */
  def extentZ: Double = (nz - 1) * dz
  
  /** Minimum velocity in model. */
  def minVelocity: Double = min(velocities)
  
  /** Maximum velocity in model. */
  def maxVelocity: Double = max(velocities)
  
  /** Mean velocity in model. */
  def meanVelocity: Double = sum(velocities) / velocities.size.toDouble
  
  /**
   * Bilinear interpolation of velocity at a given position.
   *
   * @param x Horizontal position in meters
   * @param z Vertical position in meters
   * @return Interpolated velocity value
   */
  def interpolateAt(x: Double, z: Double): Double = {
    val (x0, z0) = origin
    
    // Continuous grid indices
    val ix = (x - x0) / dx
    val iz = (z - z0) / dz
    
    // Integer indices
    val i0 = math.max(0, math.min(nz - 2, iz.toInt))
    val j0 = math.max(0, math.min(nx - 2, ix.toInt))
    val i1 = i0 + 1
    val j1 = j0 + 1
    
    // Fractional parts
    val fx = ix - j0
    val fz = iz - i0
    
    // Bilinear interpolation
    val v00 = velocities(i0, j0)
    val v01 = velocities(i0, j1)
    val v10 = velocities(i1, j0)
    val v11 = velocities(i1, j1)
    
    (1 - fx) * (1 - fz) * v00 +
    fx * (1 - fz) * v01 +
    (1 - fx) * fz * v10 +
    fx * fz * v11
  }
  
  /**
   * Convert velocity model to slowness (1/v).
   *
   * @return New VelocityModel containing slowness values
   */
  def toSlowness: VelocityModel = {
    val slowness = velocities.map(v => 1.0 / v)
    copy(velocities = slowness)
  }
  
  /**
   * Extract a horizontal slice at given depth index.
   *
   * @param depthIndex Z-index of the slice
   * @return 1D velocity profile
   */
  def horizontalSlice(depthIndex: Int): DenseVector[Double] = {
    require(depthIndex >= 0 && depthIndex < nz, "Invalid depth index")
    velocities(depthIndex, ::).t
  }
  
  /**
   * Extract a vertical slice at given horizontal index.
   *
   * @param horizontalIndex X-index of the slice
   * @return 1D velocity profile
   */
  def verticalSlice(horizontalIndex: Int): DenseVector[Double] = {
    require(horizontalIndex >= 0 && horizontalIndex < nx, "Invalid horizontal index")
    velocities(::, horizontalIndex)
  }
  
  override def toString: String = {
    val vmin = minVelocity
    val vmax = maxVelocity
    f"VelocityModel(${nz}x${nx}, v=$vmin%.0f-$vmax%.0f m/s)"
  }
}

object VelocityModel {
  
  /**
   * Create a constant velocity model.
   *
   * @param velocity Constant velocity value (m/s)
   * @param nx       Number of horizontal points
   * @param nz       Number of vertical points
   * @param dx       Horizontal spacing
   * @param dz       Vertical spacing
   */
  def constant(velocity: Double, nx: Int, nz: Int, 
               dx: Double, dz: Double): VelocityModel = {
    val grid = DenseMatrix.fill(nz, nx)(velocity)
    VelocityModel(grid, dx, dz)
  }
  
  /**
   * Create a linearly increasing velocity model (v = v0 + gradient * z).
   *
   * @param v0       Surface velocity (m/s)
   * @param gradient Velocity gradient (1/s)
   * @param nx       Number of horizontal points
   * @param nz       Number of vertical points
   * @param dx       Horizontal spacing
   * @param dz       Vertical spacing
   */
  def linear(v0: Double, gradient: Double, nx: Int, nz: Int,
             dx: Double, dz: Double): VelocityModel = {
    val grid = DenseMatrix.zeros[Double](nz, nx)
    for (i <- 0 until nz; j <- 0 until nx) {
      grid(i, j) = v0 + gradient * (i * dz)
    }
    VelocityModel(grid, dx, dz)
  }
  
  /**
   * Create from raw 2D array.
   *
   * @param data 2D array of velocity values
   * @param dx   Horizontal spacing
   * @param dz   Vertical spacing
   */
  def fromArray(data: Array[Array[Double]], dx: Double, dz: Double): VelocityModel = {
    require(data.nonEmpty, "Data array must not be empty")
    val nz = data.length
    val nx = data.head.length
    val matrix = DenseMatrix.zeros[Double](nz, nx)
    for (i <- data.indices) {
      matrix(i, ::) := DenseVector(data(i)).t
    }
    VelocityModel(matrix, dx, dz)
  }
}

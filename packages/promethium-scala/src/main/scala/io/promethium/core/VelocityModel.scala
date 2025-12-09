package io.promethium.core

import breeze.linalg._

/**
 * 2D or 3D velocity model for seismic processing.
 *
 * @param velocities 2D matrix of velocity values (m/s)
 * @param dx         Horizontal grid spacing (m)
 * @param dz         Vertical grid spacing (m)
 * @param origin     Grid origin coordinates (x0, z0)
 * @param metadata   Key-value metadata
 */
final case class VelocityModel(
  velocities: DenseMatrix[Double],
  dx: Double,
  dz: Double,
  origin: (Double, Double) = (0.0, 0.0),
  metadata: Map[String, String] = Map.empty
) {
  require(dx > 0, "dx must be positive")
  require(dz > 0, "dz must be positive")
  
  /** Number of horizontal grid points */
  def nx: Int = velocities.cols
  
  /** Number of vertical grid points */
  def nz: Int = velocities.rows
  
  /** Minimum velocity in model */
  def minVelocity: Double = min(velocities)
  
  /** Maximum velocity in model */
  def maxVelocity: Double = max(velocities)
  
  /** Mean velocity in model */
  def meanVelocity: Double = sum(velocities) / velocities.size.toDouble
  
  /**
   * Interpolate velocity at a given position.
   *
   * @param x Horizontal position
   * @param z Vertical position
   * @return Interpolated velocity value
   */
  def interpolateAt(x: Double, z: Double): Double = {
    val (x0, z0) = origin
    
    // Grid indices (floating point)
    val ix = (x - x0) / dx
    val iz = (z - z0) / dz
    
    // Clamp to valid range
    val i = math.max(0, math.min(nz - 1, iz.toInt))
    val j = math.max(0, math.min(nx - 1, ix.toInt))
    
    velocities(i, j)
  }
  
  /**
   * Convert velocity to slowness (1/v).
   *
   * @return New VelocityModel containing slowness values
   */
  def toSlowness: VelocityModel = {
    val slowness = velocities.map(v => 1.0 / v)
    copy(velocities = slowness)
  }
  
  override def toString: String = {
    val vmin = minVelocity
    val vmax = maxVelocity
    s"VelocityModel(${nz}x${nx}, v=${"%.0f".format(vmin)}-${"%.0f".format(vmax)} m/s)"
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
   * Create a linearly increasing velocity model (v0 + gradient * z).
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
}

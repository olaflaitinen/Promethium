package io.promethium.core

/**
 * Domain-specific exceptions for Promethium.
 */
sealed abstract class PromethiumException(message: String) 
  extends Exception(message)

/** Exception for I/O operations (file read/write failures). */
final case class IoException(message: String) 
  extends PromethiumException(message)

/** Exception for invalid configuration. */
final case class InvalidConfigException(message: String) 
  extends PromethiumException(message)

/** Exception when an algorithm fails to converge. */
final case class AlgorithmConvergenceException(message: String) 
  extends PromethiumException(message)

/** Exception for invalid input data. */
final case class InvalidDataException(message: String) 
  extends PromethiumException(message)

/** Exception for unsupported operations or formats. */
final case class UnsupportedOperationException(message: String) 
  extends PromethiumException(message)

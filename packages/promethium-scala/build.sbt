ThisBuild / organization := "io.promethium"
ThisBuild / version := "1.0.4"
ThisBuild / scalaVersion := "2.13.14"
ThisBuild / crossScalaVersions := Seq("2.13.14", "3.4.2")

lazy val promethiumScala = (project in file("."))
  .settings(
    name := "promethium-scala",
    description := "Promethium: Advanced Seismic Data Recovery and Reconstruction Framework for Scala/JVM",
    
    // Scala compiler options
    scalacOptions ++= Seq(
      "-deprecation",
      "-feature",
      "-unchecked",
      "-Xlint",
      "-encoding", "utf8"
    ),
    
    // Core dependencies
    libraryDependencies ++= Seq(
      // Numerical computing
      "org.scalanlp" %% "breeze" % "2.1.0",
      "org.scalanlp" %% "breeze-viz" % "2.1.0" % Optional,
      
      // Configuration
      "com.typesafe" % "config" % "1.4.3",
      
      // Logging
      "org.slf4j" % "slf4j-api" % "2.0.9",
      "ch.qos.logback" % "logback-classic" % "1.4.14" % Runtime,
      
      // JSON parsing
      "io.circe" %% "circe-core" % "0.14.6",
      "io.circe" %% "circe-generic" % "0.14.6",
      "io.circe" %% "circe-parser" % "0.14.6",
      
      // Deep Learning (optional, for ML models)
      "org.deeplearning4j" % "deeplearning4j-core" % "1.0.0-M2.1" % Optional,
      "org.nd4j" % "nd4j-native-platform" % "1.0.0-M2.1" % Optional,
      
      // Testing
      "org.scalatest" %% "scalatest" % "3.2.17" % Test,
      "org.scalatestplus" %% "scalacheck-1-17" % "3.2.17.0" % Test
    ),
    
    // Resolvers
    resolvers ++= Seq(
      "Sonatype OSS Snapshots" at "https://oss.sonatype.org/content/repositories/snapshots",
      "Sonatype OSS Releases" at "https://oss.sonatype.org/content/repositories/releases"
    ),
    
    // Publication settings
    publishMavenStyle := true,
    publishTo := {
      val nexus = "https://s01.oss.sonatype.org/"
      if (isSnapshot.value)
        Some("snapshots" at nexus + "content/repositories/snapshots")
      else
        Some("releases" at nexus + "service/local/staging/deploy/maven2")
    },
    
    licenses := Seq("CC BY-NC 4.0" -> url("https://creativecommons.org/licenses/by-nc/4.0/")),
    homepage := Some(url("https://github.com/olaflaitinen/Promethium")),
    
    scmInfo := Some(
      ScmInfo(
        url("https://github.com/olaflaitinen/Promethium"),
        "scm:git:https://github.com/olaflaitinen/Promethium.git"
      )
    ),
    
    developers := List(
      Developer(
        id = "olaflaitinen",
        name = "Promethium Contributors",
        email = "promethium@example.com",
        url = url("https://github.com/olaflaitinen/Promethium")
      )
    ),
    
    // Test settings
    Test / parallelExecution := false,
    Test / fork := true
  )

// Aliases for convenience
addCommandAlias("fmt", "scalafmtAll")
addCommandAlias("check", "scalafmtCheckAll")

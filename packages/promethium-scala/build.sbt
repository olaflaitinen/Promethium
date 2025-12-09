ThisBuild / version := "1.0.4"
ThisBuild / scalaVersion := "2.13.12"
ThisBuild / organization := "io.promethium"

lazy val root = (project in file("."))
  .settings(
    name := "promethium-scala",
    description := "Advanced Seismic Data Recovery and Reconstruction Framework for Scala/JVM",
    
    libraryDependencies ++= Seq(
      // Linear algebra
      "org.scalanlp" %% "breeze" % "2.1.0",
      "org.scalanlp" %% "breeze-viz" % "2.1.0",
      
      // Testing
      "org.scalatest" %% "scalatest" % "3.2.17" % Test
    ),
    
    // Compiler options
    scalacOptions ++= Seq(
      "-deprecation",
      "-feature",
      "-unchecked",
      "-Xlint"
    ),
    
    // Publishing settings
    licenses := Seq("CC BY-NC 4.0" -> url("https://creativecommons.org/licenses/by-nc/4.0/")),
    homepage := Some(url("https://github.com/olaflaitinen/Promethium")),
    developers := List(
      Developer(
        id = "olaflaitinen",
        name = "Olaf Yunus Laitinen Imanov",
        email = "contact@promethium.dev",
        url = url("https://github.com/olaflaitinen")
      )
    )
  )

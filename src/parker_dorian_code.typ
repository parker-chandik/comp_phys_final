#show link : it => {
  text(fill: blue,
    underline(it)
  )
}

= Code!

Hello to all who have found themselves here. You can find my and Dorian's Manim 
code below. I've also included a #link("https://www.shadertoy.com/view/W32SDD", 
"link here") to the shadertoy project which I used to make the high resolution 
version of the "flip" image for Noah's section, the code for which is also listed
here.

== #underline("Manim")
#let manim_code = read("main.py")
#raw(manim_code, lang: "python")

#pagebreak()

== #underline("Fragment Shader")
#let glsl_code = read("flip.glsl")
#raw(glsl_code, lang: "glsl")
using Documenter
using Promethium

makedocs(
    sitename = "Promethium.jl",
    format = Documenter.HTML(),
    modules = [Promethium],
    build = "../../../docs/site/julia",
    pages = [
        "Home" => "index.md",
        "API" => "api.md"
    ]
)

deploydocs(
    repo = "github.com/olaflaitinen/Promethium.jl.git",
)

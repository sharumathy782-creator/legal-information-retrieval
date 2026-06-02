fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        issue: issueText,
        category: selectedCategory
    })
})

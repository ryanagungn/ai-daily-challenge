// Sample buggy & insecure JavaScript
const API_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"; // Issue 1: Hardcoded AWS credential

function calculateTotal(cartItems, discountCode) {
    let total = 0;
    
    // Issue 2: Insecure eval for discount calculation
    let discountMultiplier = 1;
    if (discountCode) {
        discountMultiplier = eval("1 - " + discountCode);
    }

    // Issue 3: Inefficient loop and floating point precision
    for (var i = 0; i < cartItems.length; i++) {
        total += cartItems[i].price * cartItems[i].qty;
    }
    
    // Missing NaN check and unhandled floating point bug
    return total * discountMultiplier;
}

function sendTelemetry(data) {
    // Issue 4: Unhandled promise rejection
    fetch("https://analytics.example.com/log", {
        method: "POST",
        body: JSON.stringify(data)
    });
}

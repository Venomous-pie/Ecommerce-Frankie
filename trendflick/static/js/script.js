// TrendFlick JavaScript Functions

// Cart and Wishlist management
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];

// Update cart and wishlist counts
function updateCounts() {
    const cartCount = document.getElementById('cartCount');
    const wishlistCount = document.getElementById('wishlistCount');
    
    if (cartCount) {
        cartCount.textContent = cart.reduce((total, item) => total + item.quantity, 0);
    }
    
    if (wishlistCount) {
        wishlistCount.textContent = wishlist.length;
    }
}

// Add to cart function
function addToCart(productId, size = null, quantity = 1) {
    // Send AJAX request to Django backend
    fetch('/api/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            size: size,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cart = data.cart;
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCounts();
            showNotification('Item added to cart!', 'success');
        } else {
            showNotification(data.message || 'Error adding item to cart', 'error');
        }
    })
    .catch(error => {
        showNotification('Error adding item to cart', 'error');
    });
}

// Add to wishlist function
function addToWishlist(productId) {
    fetch('/api/wishlist/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            wishlist = data.wishlist;
            localStorage.setItem('wishlist', JSON.stringify(wishlist));
            updateCounts();
            showNotification('Item added to wishlist!', 'success');
        } else {
            showNotification(data.message || 'Error adding item to wishlist', 'error');
        }
    })
    .catch(error => {
        showNotification('Error adding item to wishlist', 'error');
    });
}

// Remove from cart
function removeFromCart(productId, size) {
    fetch('/api/cart/remove/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            size: size
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cart = data.cart;
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCounts();
            if (window.location.pathname.includes('cart')) {
                location.reload();
            }
        } else {
            showNotification(data.message || 'Error removing item from cart', 'error');
        }
    })
    .catch(error => {
        showNotification('Error removing item from cart', 'error');
    });
}

// Remove from wishlist
function removeFromWishlist(productId) {
    fetch('/api/wishlist/remove/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            wishlist = data.wishlist;
            localStorage.setItem('wishlist', JSON.stringify(wishlist));
            updateCounts();
            if (window.location.pathname.includes('wishlist')) {
                location.reload();
            }
        } else {
            showNotification(data.message || 'Error removing item from wishlist', 'error');
        }
    })
    .catch(error => {
        showNotification('Error removing item from wishlist', 'error');
    });
}

// Update quantity in cart
function updateQuantity(productId, size, newQuantity) {
    if (newQuantity < 1) return;

    fetch('/api/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            size: size,
            quantity: newQuantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cart = data.cart;
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCounts();
            if (window.location.pathname.includes('cart')) {
                location.reload();
            }
        } else {
            showNotification(data.message || 'Error updating quantity', 'error');
        }
    })
    .catch(error => {
        showNotification('Error updating quantity', 'error');
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    updateCounts();
    
    // Search functionality
    const searchForm = document.querySelector('form[role="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('searchInput').value.trim();
            if (query) {
                window.location.href = `/search/?q=${encodeURIComponent(query)}`;
            }
        });
    }
    
    // Newsletter subscription
    const newsletterForm = document.querySelector('form.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            if (email) {
                fetch('/api/newsletter/subscribe/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ email: email })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('Thank you for subscribing to our newsletter!', 'success');
                        this.reset();
                    } else {
                        showNotification(data.message || 'Error subscribing to newsletter', 'error');
                    }
                })
                .catch(error => {
                    showNotification('Error subscribing to newsletter', 'error');
                });
            }
        });
    }
}); 
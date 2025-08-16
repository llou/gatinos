// Skeleton loader utilities for image loading
document.addEventListener('DOMContentLoaded', function() {
    // Add skeleton loading to images that don't have src yet
    const images = document.querySelectorAll('img[data-src]');
    
    images.forEach(function(img) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-image';
        skeleton.style.position = 'absolute';
        skeleton.style.top = '0';
        skeleton.style.left = '0';
        skeleton.style.width = '100%';
        skeleton.style.height = '100%';
        
        // Make parent position relative if it isn't already
        const parent = img.parentElement;
        if (getComputedStyle(parent).position === 'static') {
            parent.style.position = 'relative';
        }
        
        // Insert skeleton before image
        parent.insertBefore(skeleton, img);
        
        // Set up image loading
        img.onload = function() {
            skeleton.remove();
            img.style.opacity = '1';
        };
        
        // Start loading the image
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
    });
    
    // Add fade-in effect for gallery images
    const galleryImages = document.querySelectorAll('.galeria-fotos-miniatura, .galeria-gatos-miniatura');
    galleryImages.forEach(function(img) {
        if (img.complete) {
            img.style.opacity = '1';
        }
    });
});

// Utility function to show skeleton for dynamic content
function showSkeleton(container, type = 'gallery') {
    const skeletonContainer = document.createElement('div');
    skeletonContainer.className = 'skeleton-container';
    
    if (type === 'gallery') {
        for (let i = 0; i < 9; i++) {
            const item = document.createElement('div');
            item.className = 'enlace-foto';
            item.innerHTML = `
                <div class="marco-foto">
                    <div class="skeleton-thumbnail"></div>
                </div>
                <div class="enlace-foto-fecha">
                    <div class="skeleton-text" style="width: 80px; height: 1em;"></div>
                </div>
            `;
            skeletonContainer.appendChild(item);
        }
    } else if (type === 'table') {
        const table = document.createElement('table');
        table.className = 'tabla-informes';
        for (let i = 0; i < 6; i++) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="titulo"><div class="skeleton-text"></div></td>
                <td class="autor"><div class="skeleton-text"></div></td>
                <td class="fecha"><div class="skeleton-text"></div></td>
                <td class="acciones"><div class="skeleton-text"></div></td>
            `;
            table.appendChild(row);
        }
        skeletonContainer.appendChild(table);
    }
    
    container.appendChild(skeletonContainer);
    return skeletonContainer;
}

// Utility function to hide skeleton
function hideSkeleton(skeletonContainer) {
    if (skeletonContainer && skeletonContainer.parentElement) {
        skeletonContainer.remove();
    }
}

// Export functions for use in other scripts
window.SkeletonLoader = {
    show: showSkeleton,
    hide: hideSkeleton
};
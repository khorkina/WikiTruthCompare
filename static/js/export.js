/**
 * WikiTruth - Export Functionality
 * Handles exporting comparison results to DOCX format
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all export buttons
    const exportButtons = document.querySelectorAll('.export-btn');
    
    // Add click event listeners
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const mode = this.dataset.mode;
            exportToDocx(mode);
        });
    });
    
    /**
     * Export comparison results to DOCX format
     * @param {string} mode - Comparison mode: 'summary', 'full', or 'funny'
     */
    function exportToDocx(mode) {
        // Make sure we have content to export
        if (!WikiTruth.comparisonResults[mode]) {
            WikiTruth.showNotification('No content available to export', 'error');
            return;
        }
        
        try {
            // Get mode title
            const modeTitle = {
                'summary': 'Key Factual Discrepancies',
                'full': 'Complete Article Comparison',
                'funny': 'Sarcastic Roast of Differences'
            }[mode];
            
            // Get current date for filename
            const date = new Date();
            const dateStr = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
            
            // Create filename
            const fileName = `WikiTruth_${mode}_${dateStr}.txt`;
            
            // Get content
            let content = WikiTruth.comparisonResults[mode];
            
            // Ensure content is a string
            if (typeof content !== 'string') {
                content = String(content || '');
            }
            
            // Create a text version of the content (simple conversion)
            content = content.replace(/<p>/g, '').replace(/<\/p>/g, '\n\n').replace(/<br>/g, '\n');
            
            // Create text blob with content
            const blob = new Blob([`# WikiTruth - ${modeTitle}\n\nGenerated on ${date.toLocaleString()}\n\n${content}`], { type: 'text/plain' });
            
            // Create download link
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            
            // Trigger download
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(function() {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }, 100);
            
            // Show success notification
            WikiTruth.showNotification(`Exported as ${fileName}`, 'success');
            
        } catch (error) {
            console.error('Export error:', error);
            WikiTruth.showNotification('Failed to export document. Please try again.', 'error');
        }
    }
});

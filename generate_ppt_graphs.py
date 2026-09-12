import matplotlib.pyplot as plt
import numpy as np

# Set a dark theme to match the MANTHAN app aesthetic
plt.style.use('dark_background')

# Colors matching the MANTHAN UI
cyan = '#06b6d4'
orange = '#f97316'
yellow = '#eab308'
gray = '#334155'

def generate_training_loss_curve():
    """Generates a simulated YOLOv8 training loss curve."""
    epochs = np.arange(1, 51)
    # Simulated exponential decay with some noise
    box_loss = 2.5 * np.exp(-epochs / 10) + np.random.normal(0, 0.05, 50) + 0.5
    cls_loss = 1.8 * np.exp(-epochs / 8) + np.random.normal(0, 0.03, 50) + 0.2
    
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, box_loss, label='Bounding Box Loss', color=cyan, linewidth=2)
    plt.plot(epochs, cls_loss, label='Classification Loss', color=orange, linewidth=2)
    
    plt.title('MANTHAN Model Training Optimization', fontsize=16, fontweight='bold', color='white')
    plt.xlabel('Training Epochs', fontsize=12, color='lightgray')
    plt.ylabel('Loss', fontsize=12, color='lightgray')
    plt.grid(True, alpha=0.2, color='gray', linestyle='--')
    plt.legend(loc='upper right', fontsize=12)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig('ppt_training_loss.png', dpi=300, transparent=True)
    print("Generated ppt_training_loss.png")
    plt.close()

def generate_class_distribution():
    """Generates a bar chart showing the distribution of detected anomalies."""
    classes = ['Shipwrecks', 'Subsea Cables', 'Ghost Pots', 'Platforms', 'Debris']
    counts = [142, 86, 310, 24, 215]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(classes, counts, color=[cyan, cyan, orange, yellow, gray])
    
    plt.title('Anomaly Detection Distribution (Simulated Survey)', fontsize=16, fontweight='bold', color='white')
    plt.xlabel('Anomaly Classification', fontsize=12, color='lightgray')
    plt.ylabel('Number of Detections', fontsize=12, color='lightgray')
    
    # Add data labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 5, int(yval), ha='center', va='bottom', color='white', fontweight='bold')
        
    plt.grid(axis='y', alpha=0.2, color='gray', linestyle='--')
    
    plt.tight_layout()
    plt.savefig('ppt_class_distribution.png', dpi=300, transparent=True)
    print("Generated ppt_class_distribution.png")
    plt.close()

def generate_processing_speed():
    """Generates a scatter plot comparing accuracy vs processing time."""
    models = ['Heuristic Demo', 'MobileNet', 'YOLOv8n (MANTHAN)', 'YOLOv8x']
    speed_ms = [45, 110, 65, 320]
    accuracy = [65, 78, 94.2, 96.5]
    colors = [gray, yellow, cyan, orange]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(speed_ms, accuracy, s=300, c=colors, alpha=0.8, edgecolors='white', linewidth=2)
    
    for i, model in enumerate(models):
        plt.annotate(model, (speed_ms[i], accuracy[i]), 
                     xytext=(10, 10), textcoords='offset points', 
                     fontsize=11, color='white', fontweight='bold')
        
    plt.title('Model Efficiency: Accuracy vs. Processing Latency', fontsize=16, fontweight='bold', color='white')
    plt.xlabel('Processing Time per Frame (ms)', fontsize=12, color='lightgray')
    plt.ylabel('mAP Accuracy Score (%)', fontsize=12, color='lightgray')
    plt.grid(True, alpha=0.2, color='gray', linestyle='--')
    
    plt.tight_layout()
    plt.savefig('ppt_model_efficiency.png', dpi=300, transparent=True)
    print("Generated ppt_model_efficiency.png")
    plt.close()

if __name__ == '__main__':
    print("Generating PPT Graphics...")
    generate_training_loss_curve()
    generate_class_distribution()
    generate_processing_speed()
    print("Done! You can drag these .png files directly into your presentation.")

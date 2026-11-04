import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_system_architecture():
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.axis('off')
    
    # Styles
    box_blue = dict(boxstyle="round,pad=0.5", fc="#EBF5FB", ec="#2980B9", lw=1.5)
    box_white = dict(boxstyle="round,pad=0.4", fc="#FFFFFF", ec="#7F8C8D", lw=1.2)
    box_header = dict(boxstyle="round,pad=0.5", fc="#2C3E50", ec="#1A252F", lw=1.5)
    
    # User Layer
    ax.text(0.5, 0.93, "User (Customer / Administrator)\nDesktop or Mobile Device", 
            ha='center', va='center', fontsize=10, weight='bold', bbox=box_blue)
    
    ax.annotate("", xy=(0.5, 0.84), xytext=(0.5, 0.88),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#2C3E50"))
    ax.text(0.52, 0.86, "1. Request / Response", fontsize=8, color="#34495E")
    
    # Browser
    ax.text(0.5, 0.81, "Web Browser (Chrome, Edge, Firefox, Safari)", 
            ha='center', va='center', fontsize=9.5, weight='bold', bbox=box_white)
    
    ax.annotate("", xy=(0.5, 0.72), xytext=(0.5, 0.77),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#2C3E50"))
    ax.text(0.52, 0.745, "2. Renders Dynamic UI", fontsize=8, color="#34495E")
    
    # Presentation Layer Container
    rect_pres = patches.FancyBboxPatch((0.08, 0.58), 0.84, 0.12, boxstyle="round,pad=0.02",
                                        fc="#F8F9F9", ec="#BDC3C7", ls="--", lw=1.2)
    ax.add_patch(rect_pres)
    ax.text(0.5, 0.68, "Presentation Layer (Client-Side)", ha='center', fontsize=9, weight='bold', color="#2C3E50")
    
    ax.text(0.23, 0.62, "HTML5\nPage Structure & Semantics", ha='center', va='center', fontsize=8, bbox=box_white)
    ax.text(0.50, 0.62, "CSS3 & Bootstrap 5\nResponsive Theme & Layout", ha='center', va='center', fontsize=8, bbox=box_white)
    ax.text(0.77, 0.62, "Vanilla JavaScript\nValidation, Modals & Live Search", ha='center', va='center', fontsize=8, bbox=box_white)
    
    ax.annotate("", xy=(0.5, 0.49), xytext=(0.5, 0.57),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#2C3E50"))
    ax.text(0.52, 0.53, "3. HTTP Requests (POST / GET)", fontsize=8, color="#34495E")
    
    # Application Layer Container
    rect_app = patches.FancyBboxPatch((0.05, 0.28), 0.90, 0.19, boxstyle="round,pad=0.02",
                                       fc="#F4F6F6", ec="#3498DB", lw=1.5)
    ax.add_patch(rect_app)
    ax.text(0.5, 0.445, "Application Layer: Apache HTTP Server + PHP 8 (XAMPP Environment)", 
            ha='center', fontsize=9.5, weight='bold', color="#1B4F72")
    
    modules = [
        "Authentication &\nSession RBAC",
        "Vehicle Fleet\nManagement",
        "Service Booking &\nPricing Engine",
        "Admin Dispatch &\nQueue Management",
        "Revenue Metrics &\nCustomer Directory"
    ]
    xs = [0.14, 0.32, 0.50, 0.68, 0.86]
    for x, mod in zip(xs, modules):
        ax.text(x, 0.35, mod, ha='center', va='center', fontsize=7.5, weight='semibold', bbox=box_white)
        
    ax.annotate("", xy=(0.5, 0.19), xytext=(0.5, 0.27),
                arrowprops=dict(arrowstyle="<->", lw=1.5, color="#2C3E50"))
    ax.text(0.52, 0.23, "4. PDO Prepared Statements (SQL / utf8mb4)", fontsize=8, color="#34495E")
    
    # Data Layer Container
    rect_data = patches.FancyBboxPatch((0.15, 0.04), 0.70, 0.13, boxstyle="round,pad=0.02",
                                        fc="#EAEDED", ec="#16A085", lw=1.5)
    ax.add_patch(rect_data)
    ax.text(0.5, 0.14, "Data Storage Layer (Relational MySQL Database: vehicle_service_db)", 
            ha='center', fontsize=9.5, weight='bold', color="#0E6251")
    
    tables = ["users", "vehicles", "services", "service_requests"]
    txs = [0.25, 0.41, 0.58, 0.75]
    for tx, tbl in zip(txs, tables):
        ax.text(tx, 0.08, f"Table: {tbl}", ha='center', va='center', fontsize=8, weight='bold', 
                bbox=dict(boxstyle="square,pad=0.3", fc="#FFFFFF", ec="#16A085", lw=1))
        
    plt.tight_layout()
    plt.savefig(r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_3_1_system_architecture.png", dpi=300)
    plt.close()

def draw_er_diagram():
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)
    ax.axis('off')
    
    tbl_header = dict(boxstyle="square,pad=0.3", fc="#1B4F72", ec="#1B4F72", lw=1.2)
    tbl_body = dict(boxstyle="square,pad=0.4", fc="#F8F9F9", ec="#2C3E50", lw=1.2)
    
    # Users Table
    ax.text(0.20, 0.88, "users", ha='center', va='center', fontsize=9, weight='bold', color="white", bbox=tbl_header)
    users_text = "id (PK)\nname\nemail (UNIQUE)\nphone\npassword_hash\naddress\nrole ('admin','customer')\ncreated_at"
    ax.text(0.20, 0.67, users_text, ha='center', va='center', fontsize=7.5, family='monospace', bbox=tbl_body)
    
    # Vehicles Table
    ax.text(0.80, 0.88, "vehicles", ha='center', va='center', fontsize=9, weight='bold', color="white", bbox=tbl_header)
    vehicles_text = "id (PK)\nuser_id (FK -> users.id)\nvehicle_type\nbrand\nmodel\nreg_number (UNIQUE)\nyear\nfuel_type\ncreated_at"
    ax.text(0.80, 0.66, vehicles_text, ha='center', va='center', fontsize=7.5, family='monospace', bbox=tbl_body)
    
    # Services Table
    ax.text(0.20, 0.35, "services", ha='center', va='center', fontsize=9, weight='bold', color="white", bbox=tbl_header)
    services_text = "id (PK)\nservice_name\ndescription\nbase_price\ncreated_at"
    ax.text(0.20, 0.21, services_text, ha='center', va='center', fontsize=7.5, family='monospace', bbox=tbl_body)
    
    # Service Requests Table
    ax.text(0.78, 0.35, "service_requests", ha='center', va='center', fontsize=9, weight='bold', color="white", bbox=tbl_header)
    requests_text = "id (PK)\nuser_id (FK -> users.id)\nvehicle_id (FK -> vehicles.id)\nservice_id (FK -> services.id)\npreferred_date\ndescription\nstatus (Pending/In Progress/..)\nadmin_remark\ncost\ncreated_at / updated_at"
    ax.text(0.78, 0.16, requests_text, ha='center', va='center', fontsize=7.5, family='monospace', bbox=tbl_body)
    
    # Connectors & Cardinalities
    # users -> vehicles
    ax.annotate("", xy=(0.67, 0.68), xytext=(0.33, 0.68),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#2C3E50"))
    ax.text(0.50, 0.70, "owns (1 : N)", ha='center', fontsize=8, weight='bold', color="#2980B9")
    
    # users -> service_requests
    ax.annotate("", xy=(0.64, 0.25), xytext=(0.28, 0.53),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#2C3E50"))
    ax.text(0.42, 0.41, "submits (1 : N)", ha='center', fontsize=8, weight='bold', color="#2980B9")
    
    # vehicles -> service_requests
    ax.annotate("", xy=(0.78, 0.32), xytext=(0.80, 0.49),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#2C3E50"))
    ax.text(0.85, 0.40, "services (1 : N)", ha='left', fontsize=8, weight='bold', color="#2980B9")
    
    # services -> service_requests
    ax.annotate("", xy=(0.64, 0.16), xytext=(0.32, 0.16),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#2C3E50"))
    ax.text(0.48, 0.18, "categorizes (1 : N)", ha='center', fontsize=8, weight='bold', color="#2980B9")
    
    plt.tight_layout()
    plt.savefig(r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_3_2_er_diagram.png", dpi=300)
    plt.close()

def draw_flowchart():
    fig, ax = plt.subplots(figsize=(8.5, 9.5), dpi=300)
    ax.axis('off')
    
    oval = dict(boxstyle="round,pad=0.5", fc="#D4EFDF", ec="#27AE60", lw=1.5)
    box = dict(boxstyle="square,pad=0.4", fc="#EBF5FB", ec="#2980B9", lw=1.2)
    diamond = dict(boxstyle="round4,pad=0.4", fc="#FCF3CF", ec="#F39C12", lw=1.2)
    
    ax.text(0.5, 0.96, "Start", ha='center', va='center', fontsize=9.5, weight='bold', bbox=oval)
    
    steps = [
        (0.88, "Customer Logs in & navigates to 'Book Service'"),
        (0.79, "Selects Registered Vehicle & Chooses Service Package"),
        (0.70, "System fetches Service Base Cost & displays Live Preview"),
        (0.61, "Customer specifies Preferred Date & Problem Description"),
    ]
    for y, text in steps:
        ax.text(0.5, y, text, ha='center', va='center', fontsize=8.5, bbox=box)
        
    ax.text(0.5, 0.49, "Valid Input & Date\n>= Today?", ha='center', va='center', fontsize=8.5, weight='bold', bbox=diamond)
    
    ax.text(0.85, 0.49, "Show Form Validation\nError Alert", ha='center', va='center', fontsize=8, bbox=box)
    
    ax.text(0.5, 0.37, "Insert Record into 'service_requests' (Status: 'Pending')", ha='center', va='center', fontsize=8.5, bbox=box)
    ax.text(0.5, 0.27, "Admin Reviews Ticket in Service Queue & Dispatches Mechanic\n(Status updated to 'In Progress')", ha='center', va='center', fontsize=8.5, bbox=box)
    ax.text(0.5, 0.16, "Service Finished: Admin enters Diagnostic Remarks & Total Cost\n(Status updated to 'Completed')", ha='center', va='center', fontsize=8.5, bbox=box)
    ax.text(0.5, 0.07, "Customer views Final Bill & Remarks in 'Service History'", ha='center', va='center', fontsize=8.5, bbox=box)
    
    ax.text(0.5, 0.01, "End", ha='center', va='center', fontsize=9.5, weight='bold', bbox=oval)
    
    # Arrows
    ys = [0.96, 0.88, 0.79, 0.70, 0.61]
    for i in range(len(ys)-1):
        ax.annotate("", xy=(0.5, ys[i+1]+0.025), xytext=(0.5, ys[i]-0.025),
                    arrowprops=dict(arrowstyle="->", lw=1.2, color="#2C3E50"))
        
    ax.annotate("", xy=(0.5, 0.54), xytext=(0.5, 0.58),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#2C3E50"))
    
    # Diamond connections
    ax.annotate("", xy=(0.73, 0.49), xytext=(0.63, 0.49),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#C0392B"))
    ax.text(0.67, 0.51, "No", fontsize=8, weight='bold', color="#C0392B")
    
    ax.annotate("", xy=(0.5, 0.40), xytext=(0.5, 0.44),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#27AE60"))
    ax.text(0.52, 0.42, "Yes", fontsize=8, weight='bold', color="#27AE60")
    
    # Lower arrows
    low_ys = [0.37, 0.27, 0.16, 0.07, 0.01]
    for i in range(len(low_ys)-1):
        ax.annotate("", xy=(0.5, low_ys[i+1]+0.025), xytext=(0.5, low_ys[i]-0.025),
                    arrowprops=dict(arrowstyle="->", lw=1.2, color="#2C3E50"))
        
    plt.tight_layout()
    plt.savefig(r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_3_3_flowchart_booking.png", dpi=300)
    plt.close()

def draw_typical_workflow():
    fig, ax = plt.subplots(figsize=(8.5, 10.5), dpi=300)
    ax.axis('off')
    
    oval = dict(boxstyle="round,pad=0.4", fc="#D4EFDF", ec="#27AE60", lw=1.2)
    box = dict(boxstyle="square,pad=0.35", fc="#EBF5FB", ec="#2980B9", lw=1.1)
    diamond = dict(boxstyle="round4,pad=0.35", fc="#FCF3CF", ec="#F39C12", lw=1.1)
    admin_box = dict(boxstyle="square,pad=0.35", fc="#FADBD8", ec="#E74C3C", lw=1.1)
    
    ax.text(0.5, 0.98, "Open VSM Pro Web Application", ha='center', va='center', fontsize=9, weight='bold', bbox=oval)
    ax.text(0.5, 0.91, "Already Registered?", ha='center', va='center', fontsize=8.5, weight='bold', bbox=diamond)
    
    ax.text(0.82, 0.91, "Register New Account\n(Client/Server Validated)", ha='center', va='center', fontsize=7.5, bbox=box)
    ax.text(0.5, 0.83, "User Sign In (Email & Password Hash Verification)", ha='center', va='center', fontsize=8.5, bbox=box)
    ax.text(0.5, 0.74, "Check Role in Session?", ha='center', va='center', fontsize=8.5, weight='bold', bbox=diamond)
    
    # Branch Customer (Left) vs Admin (Right)
    # Customer branch
    ax.text(0.26, 0.65, "Customer Portal Dashboard", ha='center', va='center', fontsize=8.5, weight='bold', bbox=box)
    ax.text(0.26, 0.55, "Register & Manage Fleet\n(Add, Edit, View Vehicles)", ha='center', va='center', fontsize=7.5, bbox=box)
    ax.text(0.26, 0.44, "Book Service Appointment\n(Vehicle, Package, Date, Notes)", ha='center', va='center', fontsize=7.5, bbox=box)
    ax.text(0.26, 0.33, "Service Request History\n(Track Status: Pending / In Progress /\nCompleted / Cancelled)", ha='center', va='center', fontsize=7.5, bbox=box)
    ax.text(0.26, 0.21, "Optional: Cancel Pending Request\nOr View Finalized Bill & Remarks", ha='center', va='center', fontsize=7.5, bbox=box)
    
    # Admin branch
    ax.text(0.74, 0.65, "Admin Management Console", ha='center', va='center', fontsize=8.5, weight='bold', bbox=admin_box)
    ax.text(0.74, 0.55, "View Live Workshop Metrics\n(Fleet, Active Queue, Revenue)", ha='center', va='center', fontsize=7.5, bbox=admin_box)
    ax.text(0.74, 0.44, "Service Request Queue\n(Filter by Status, Search Records)", ha='center', va='center', fontsize=7.5, bbox=admin_box)
    ax.text(0.74, 0.33, "Dispatch & Update Service Ticket\n(Set In Progress / Completed, Remarks, Cost)", ha='center', va='center', fontsize=7.5, bbox=admin_box)
    ax.text(0.74, 0.21, "Customer Directory & Fleet Roster\n(Inspect Customer Vehicles & Contacts)", ha='center', va='center', fontsize=7.5, bbox=admin_box)
    
    # Convergence
    ax.text(0.5, 0.10, "Secure Sign Out (Destroy Session & Clear Tokens)", ha='center', va='center', fontsize=8.5, bbox=box)
    ax.text(0.5, 0.02, "Exit Application", ha='center', va='center', fontsize=9, weight='bold', bbox=oval)
    
    # Connections
    ax.annotate("", xy=(0.5, 0.94), xytext=(0.5, 0.96), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(0.72, 0.91), xytext=(0.60, 0.91), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.text(0.65, 0.925, "No", fontsize=7.5, color="#C0392B", weight='bold')
    
    ax.annotate("", xy=(0.82, 0.855), xytext=(0.82, 0.88), arrowprops=dict(arrowstyle="-", lw=1.1))
    ax.annotate("", xy=(0.67, 0.83), xytext=(0.82, 0.83), arrowprops=dict(arrowstyle="->", lw=1.1))
    
    ax.annotate("", xy=(0.5, 0.86), xytext=(0.5, 0.88), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.text(0.52, 0.87, "Yes", fontsize=7.5, color="#27AE60", weight='bold')
    
    ax.annotate("", xy=(0.5, 0.77), xytext=(0.5, 0.80), arrowprops=dict(arrowstyle="->", lw=1.1))
    
    # From Role diamond
    ax.annotate("", xy=(0.26, 0.68), xytext=(0.38, 0.74), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.text(0.28, 0.72, "Role: Customer", fontsize=7.5, weight='bold', color="#2980B9")
    
    ax.annotate("", xy=(0.74, 0.68), xytext=(0.62, 0.74), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.text(0.66, 0.72, "Role: Admin", fontsize=7.5, weight='bold', color="#C0392B")
    
    # Customer column arrows
    c_ys = [0.65, 0.55, 0.44, 0.33, 0.21]
    for i in range(len(c_ys)-1):
        ax.annotate("", xy=(0.26, c_ys[i+1]+0.035), xytext=(0.26, c_ys[i]-0.035), arrowprops=dict(arrowstyle="->", lw=1.1))
        
    # Admin column arrows
    a_ys = [0.65, 0.55, 0.44, 0.33, 0.21]
    for i in range(len(a_ys)-1):
        ax.annotate("", xy=(0.74, a_ys[i+1]+0.035), xytext=(0.74, a_ys[i]-0.035), arrowprops=dict(arrowstyle="->", lw=1.1))
        
    # Converge to sign out
    ax.annotate("", xy=(0.42, 0.12), xytext=(0.26, 0.17), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(0.58, 0.12), xytext=(0.74, 0.17), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(0.5, 0.04), xytext=(0.5, 0.075), arrowprops=dict(arrowstyle="->", lw=1.1))
    
    plt.tight_layout()
    plt.savefig(r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_3_4_typical_workflow.png", dpi=300)
    plt.close()

if __name__ == '__main__':
    print("Generating diagrams...")
    draw_system_architecture()
    draw_er_diagram()
    draw_flowchart()
    draw_typical_workflow()
    print("Diagrams successfully generated in report_assets.")

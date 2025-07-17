# Ansible Tower Workflow Template Project

This guide outlines the design and implementation of an Ansible Tower (now a component of Red Hat Ansible Automation Platform) Workflow Template project. Workflow Templates allow you to chain multiple Job Templates and other workflows together, creating complex, multi-step automation processes with conditional logic.

## Table of Contents

- [Introduction to Ansible Tower Workflow Templates](#introduction-to-ansible-tower-workflow-templates)
- [Key Components in Ansible Tower](#key-components-in-ansible-tower)
- [Architecture Overview of a Workflow Template](#architecture-overview-of-a-workflow-template)
- [Step-by-Step Guide to Creating a Workflow Template](#step-by-step-guide-to-creating-a-workflow-template)
  - [Step 1: Create/Verify Ansible Tower Components](#step-1-createverify-ansible-tower-components)
  - [Step 2: Create the Workflow Template](#step-2-create-the-workflow-template)
  - [Step 3: Design the Workflow (Visualizer)](#step-3-design-the-workflow-visualizer)
- [Benefits of Workflow Templates](#benefits-of-workflow-templates)
- [Diagrams](#diagrams)
- [Contributing](#contributing)
- [License](#license)

## Introduction to Ansible Tower Workflow Templates

A Workflow Template in Ansible Tower is a visual and logical representation of a series of automation jobs. It enables you to:

*   **Chain Jobs:** Execute multiple Ansible playbooks (defined as Job Templates) in a specific sequence.
*   **Conditional Logic:** Define success/failure paths, allowing different jobs to run based on the outcome of a previous job.
*   **Parallel Execution:** Run multiple jobs concurrently.
*   **Centralized Orchestration:** Manage complex automation flows from a single interface.
*   **Reusability:** Reuse existing Job Templates within different workflows.

## Key Components in Ansible Tower

Before creating a Workflow Template, you'll typically need these foundational components:

*   **Projects:** Define where Ansible playbooks are stored (e.g., a Git repository).
*   **Inventories:** Define the hosts (servers) that Ansible will manage.
*   **Credentials:** Store sensitive information (SSH keys, cloud API keys, vault passwords) securely.
*   **Job Templates:** Define how a specific Ansible playbook should be executed (which project, inventory, credentials, extra variables). These are the building blocks of a workflow.

## Architecture Overview of a Workflow Template

*(Diagram Placeholder: A high-level diagram showing the flow of a Workflow Template. Nodes represent Job Templates or other Workflow Templates, and arrows represent success/failure/always paths. Example: "Provision Infra" -> (Success) "Deploy App" -> (Success) "Run Tests" -> (Success) "Notify Success" / (Failure) "Rollback Infra" -> "Notify Failure")*

## Step-by-Step Guide to Creating a Workflow Template

### Prerequisites:

*   A running Ansible Tower/Automation Platform instance.
*   Necessary permissions to create Projects, Inventories, Credentials, Job Templates, and Workflow Templates.
*   Ansible playbooks already committed to a Git repository that Tower can access.

### Step 1: Create/Verify Ansible Tower Components

Ensure you have the following set up in Ansible Tower:

1.  **Project:**
    *   Go to **Resources -> Projects**.
    *   Click **"Add"**.
    *   Provide a **Name**, select **SCM Type** (e.g., Git), and enter the **SCM URL** (your Git repository containing playbooks).
    *   Save and then **"Update Project"** to sync playbooks.
2.  **Inventory:**
    *   Go to **Resources -> Inventories**.
    *   Click **"Add" -> "Add Inventory"**.
    *   Provide a **Name**.
    *   Add hosts to the inventory (manually, from SCM, or cloud sources).
3.  **Credentials:**
    *   Go to **Resources -> Credentials**.
    *   Click **"Add"**.
    *   Create credentials for:
        *   **Machine Credential:** For SSH access to your managed hosts (Type: `Machine`, Input Type: `SSH Private Key`).
        *   **Source Control Credential:** If your Git repository is private (Type: `Source Control`).
        *   (Optional) Cloud credentials (AWS, Azure, GCP) if provisioning infrastructure.
4.  **Job Templates:**
    *   Go to **Resources -> Templates**.
    *   Click **"Add" -> "Add Job Template"**.
    *   Create individual Job Templates for each distinct task you want to automate. For example:
        *   `Provision Infrastructure` (e.g., runs `provision.yml` playbook)
        *   `Deploy Application` (e.g., runs `deploy.yml` playbook)
        *   `Run Integration Tests` (e.g., runs `test.yml` playbook)
        *   `Rollback Application` (e.g., runs `rollback.yml` playbook)
        *   `Notify Success` (e.g., runs `notify_success.yml` playbook)
        *   `Notify Failure` (e.g., runs `notify_failure.yml` playbook)
    *   For each Job Template, select the **Project**, **Inventory**, **Playbook**, and **Credentials**.

### Step 2: Create the Workflow Template

1.  Go to **Resources -> Templates**.
2.  Click **"Add" -> "Add Workflow Template"**.
3.  **Details Tab:**
    *   **Name:** Provide a descriptive name (e.g., `CI/CD Pipeline for My App`).
    *   **Description:** Explain the purpose of the workflow.
    *   **Inventory:** (Optional) You can set a default inventory for the entire workflow, or let individual Job Templates define their own.
    *   **Webhook Service:** (Optional) Configure if you want to trigger this workflow from a Git webhook.
    *   Save the template.

### Step 3: Design the Workflow (Visualizer)

1.  After saving the Workflow Template, click on the **"Visualizer"** tab.
2.  **Add Nodes:**
    *   Click the **"Start"** node.
    *   Click **"Add Node"**.
    *   Select the first **Job Template** you want to run (e.g., `Provision Infrastructure`).
    *   Choose the **Run Type** (e.g., `On Success`, `On Failure`, `Always`). For the first node, it's usually `On Success` from "Start".
    *   Click **"Select"**.
3.  **Chain Nodes with Conditional Logic:**
    *   Click on the newly added node (`Provision Infrastructure`).
    *   Click **"Add Node"**.
    *   Select the next **Job Template** (e.g., `Deploy Application`).
    *   Set the **Run Type** to `On Success` (meaning `Deploy Application` runs only if `Provision Infrastructure` succeeds).
    *   Repeat this process to build out your success path (e.g., `Deploy App` -> `Run Integration Tests`).
    *   **Add Failure Paths:** From a critical node (e.g., `Deploy Application`), click **"Add Node"** again, but this time select **Run Type: `On Failure`** and choose a Job Template like `Rollback Application` or `Notify Failure`.
    *   **Add Parallel Paths:** From a node, you can add multiple "On Success" or "Always" nodes to run jobs concurrently.
    *   **Add Notification Nodes:** Include Job Templates that send notifications (e.g., to Slack, email) on success or failure of the overall workflow or specific critical stages.

## Benefits of Workflow Templates

*   **Orchestration of Complex Processes:** Manage multi-stage deployments, infrastructure provisioning, and testing in a single, coherent flow.
*   **Reduced Manual Intervention:** Automate conditional execution and error handling.
*   **Improved Visibility:** The visualizer provides a clear overview of the automation process and its current status.
*   **Enhanced Reliability:** Consistent execution paths reduce human error.
*   **Auditing and Reporting:** Tower provides detailed logs and reports for every job and workflow execution.

## Diagrams

To fully illustrate an Ansible Tower Workflow Template, visual diagrams are essential. Since I cannot directly generate and embed visual diagrams, here's how you can create and integrate them:

### How to Create and Embed Diagrams:

1.  **Choose a Diagramming Tool:**
    *   **Ansible Tower Visualizer:** The built-in visualizer is the best source. Take screenshots of your actual workflow.
    *   **Lucidchart, draw.io (diagrams.net), Miro:** Online tools with extensive shape libraries for flowcharts and architecture diagrams.
    *   **PlantUML, Mermaid:** Text-based diagramming tools that allow you to define diagrams using code, which can be version-controlled alongside your documentation.

2.  **Design the Diagrams:**

    *   **Diagram 1: High-Level Workflow Template Flow:**
        *   **Purpose:** Show the overall sequence of jobs and conditional paths.
        *   **Content:** Nodes representing Job Templates (e.g., "Build App", "Deploy Dev", "Run Tests", "Deploy Prod", "Rollback", "Notify"), connected by arrows indicating `On Success`, `On Failure`, or `Always` transitions.
        *   **Example Flow:**
            *   Start -> Build App (On Success) -> Deploy Dev (On Success) -> Run Tests (On Success) -> Deploy Prod (On Success) -> Notify Success
            *   From any failed node: (On Failure) -> Notify Failure
            *   From Deploy Prod (On Failure) -> Rollback App (On Success) -> Notify Failure
        *   *Tools:* Screenshot from Tower Visualizer, or recreate in a diagramming tool.

    *   **Diagram 2: Ansible Tower Component Relationships:**
        *   **Purpose:** Illustrate how Projects, Inventories, Credentials, and Job Templates feed into a Workflow Template.
        *   **Content:** Boxes for each component type, with arrows showing their relationships (e.g., "Project" -> "Job Template", "Inventory" -> "Job Template", "Credentials" -> "Job Template", multiple "Job Templates" -> "Workflow Template").
        *   *Tools:* Lucidchart, draw.io.

3.  **Export and Embed:**
    *   Export your diagrams as high-resolution images (e.g., PNG, SVG).
    *   Save the images in a dedicated `images/` directory within your repository.
    *   Embed the images in the `README.md` using Markdown syntax:
        ```markdown
        ### High-Level Workflow Template Flow
        ![Workflow Template Flow](images/workflow_flow.png)

        ### Ansible Tower Component Relationships
        ![Tower Components](images/tower_components.png)
        ```

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).

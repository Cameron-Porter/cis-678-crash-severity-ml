# cis-678-crash-severity-ml
Machine learning project predicting motor vehicle crash severity using NHTSA CRSS data (2020–2024), comparing Logistic Regression, Random Forest, and XGBoost.

## Branching and Pull Request Workflow

To keep `main` stable and avoid conflicts, all team members should work on separate feature branches and submit pull requests (PRs) before merging changes.

### 1. Create a Feature Branch

Before starting work, make sure your local `main` branch is up to date:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

Use descriptive branch names, such as:
- `feature/data-preprocessing`
- `feature/logistic-regression`
- `feature/random-forest`
- `feature/model-evaluation`

### 2. Commit and Push Changes

Make changes on your feature branch, then commit and push them to GitHub:

```bash
git add .
git commit -m "feat: describe your changes"
git push -u origin feature/your-feature-name
```

Commit regularly with meaningful messages.

### 3. When to Create a Pull Request

Create a pull request when:
- A feature or assigned task is complete and ready for review.
- Your code runs successfully and has been tested.
- You want feedback on work in progress (use a **Draft PR**).
- You're ready to integrate your changes into `main`.

Avoid creating one massive pull request at the end of the project. Smaller, focused PRs are easier to review and merge.

### 4. How to Create a Pull Request

1. Open the repository on GitHub.
2. Navigate to **Pull requests → New pull request**.
3. Set the **base branch** to `main`.
4. Set the **compare branch** to your feature branch.
5. Provide a descriptive title and summary of your changes.
6. Assign another team member as a reviewer.
7. Select **Create pull request**.

### 5. Review and Merge

Before merging:
- At least one other team member should review and approve the PR.
- Address any requested changes or comments.
- Confirm the changes don't break existing functionality.
- Resolve merge conflicts if necessary.

Once approved, select **Squash and merge** to merge into `main`.

**Do not push directly to `main`.** All changes should go through the pull request process.

### 6. Sync Your Local Repository

After a PR is merged, update your local `main` before starting your next task:

```bash
git checkout main
git pull origin main
git checkout -b feature/next-task
```

This ensures new work starts from the latest shared code.

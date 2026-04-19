# Project 1: E-Commerce Predictive Model

**Skills:** Applying AI and Machine Learning Concepts + Training and Deploying Models with AWS SageMaker
* **Duration:** ~2 weeks
* **Team Size:** Individual
* **Delivery:** Presentation + deployed SageMaker endpoint(s)

---

## Scenario

You are on the ML team at an e-commerce company. You have been given a dataset of 50,000 completed orders that includes order details, customer browsing behavior, and customer purchase history.

The dataset also contains three forward-looking outcomes that you **cannot know at order time** -- they represent things that haven't happened yet when the order is placed:
- How much the customer will spend over the next 90 days
- Whether the customer will stop buying within 60 days
- Whether this specific order will be returned

These are the kinds of predictions that justify ML -- you can't look them up, you can't calculate them from business rules, and the patterns are complex enough that simple heuristics won't cut it.

The dataset is in `data/ecommerce_purchases.csv`. See `data/README.md` for the full schema.

Your job: build at least one predictive model using SageMaker's built-in XGBoost algorithm, deploy it to a real-time endpoint, and understand it well enough to explain to someone else what data it needs and what its predictions mean.

---

## Choose Your Prediction Task(s)

Pick **at least one** target. You may train models for all three if you want -- each additional model costs minimal training time (~2-5 minutes per run on `ml.m5.xlarge`). Just deploy and delete **one endpoint at a time** to stay within the free tier inference budget.

| Task | Target | Type | Why it needs ML |
|---|---|---|---|
| **Customer Lifetime Value** | `customer_ltv_90d` | Regression | Future spend depends on nonlinear interactions between engagement patterns, purchase frequency, category preferences, and account maturity. No formula captures this. |
| **Churn Prediction** | `churned_within_60d` (0/1) | Binary classification | Churn signals are subtle -- a drop in sessions, fewer cart adds, longer gaps between purchases. The pattern varies by customer segment. |
| **Return Prediction** | `returned_order` (0/1) | Binary classification | Return risk depends on category, order size, browsing hesitation (cart removals), address mismatch, and customer return history interacting together. |

For each target you train, **drop the other two target columns** plus `order_id` and `user_id` from your features.

---

## Requirements

### Phase A -- Model Development (AIML Skills)

| # | Requirement |
|---|---|
| A1 | **EDA Notebook** -- Load the dataset. Profile feature distributions. For your chosen target(s), identify class balance (classification) or distribution shape (regression). Visualize at least 3 feature-target relationships. Identify which features appear most correlated with your target(s). |
| A2 | **Data Preparation** -- Encode categorical columns (`primary_category`, `payment_method`, `currency`, `primary_device`) to numeric. Drop identifiers and non-target outcome columns. Perform a train/validation/test split (70/15/15) with `random_state=42`. For classification targets, use stratified splitting. |
| A3 | **Baseline Model** -- Train a simple baseline locally (e.g., `DummyClassifier` / `LogisticRegression` for classification, mean predictor / `LinearRegression` for regression). Report metrics on the validation set. This establishes the floor that XGBoost must beat. |
| A4 | **XGBoost Training on SageMaker** -- Format the training data for SageMaker's built-in XGBoost (target column first, no headers, numeric only). Upload to S3. Configure and launch a training job using `sagemaker.estimator.Estimator` with the XGBoost `image_uri`. Set at least these hyperparameters: `objective`, `num_round`, `max_depth`, `eta`. |
| A5 | **Evaluation** -- Pull model artifacts, load locally or use Batch Transform on the test set. Report: |
| | - **Classification:** Precision, Recall, F1, AUC-ROC, Confusion Matrix | |
| | - **Regression:** RMSE, MAE, R² | |
| | Compare against your baseline. Explain why your primary metric matters for this business problem. | |
| A6 | **Explainability** -- Generate SHAP summary plots for the XGBoost model. Identify the top 5 features driving predictions. Interpret each in business terms (e.g., "high `user_cart_removals_7d` signals purchase hesitation, which correlates with higher return risk"). |

### Phase B -- SageMaker Deployment

| # | Requirement | Grading Weight |
|---|---|---|
| B1 | **S3 & IAM Setup** -- Create an S3 bucket with organized prefixes (`data/train/`, `data/test/`, `output/`). Configure a least-privilege IAM execution role scoped to your bucket. |
| B2 | **Model Registry** -- Register the trained model in a Model Package Group. Set status to `PendingManualApproval`, then approve. |
| B3 | **Deploy to Endpoint** -- Deploy to a real-time endpoint (`ml.m5.xlarge`). Invoke with `boto3` using a sample CSV payload. Verify the prediction is reasonable. |
| B4 | **Cleanup** -- Delete the endpoint, endpoint configuration, and model after presentation. Demonstrate or screenshot the cleanup. |

**Cost management:** Each `ml.m5.xlarge` endpoint costs ~$0.23/hr. Deploy one endpoint at a time. Test it, verify predictions, then delete before deploying the next. Don't leave endpoints running overnight. If you train all three targets, you can register all three in Model Registry but only deploy one at a time.

---

## Presentation (10-15 minutes)

1. **Problem choice** -- Which target(s) did you pick and why? What business value does the prediction provide?
2. **EDA highlights** -- What patterns did you find? Which features looked promising?
3. **Baseline vs. XGBoost** -- Metrics side by side. How much did XGBoost improve over the baseline?
4. **SHAP analysis** -- Which features matter most? Are they behavioral (browsing signals), historical (purchase patterns), or order-level (category, price)?
5. **Live endpoint demo** -- Invoke your deployed endpoint with a sample row and interpret the result.
6. **Reflection** -- What would you improve with more time? How would more data (from a streaming pipeline) change the model?

---

## What You Carry Into Project 2

At the end of Project 1, you will have:

- One or more **model artifacts** (`model.tar.gz`) stored in S3
- **Registered, approved model version(s)** in Model Registry
- Your **SHAP analysis** identifying which features drive predictions
- Understanding of the **endpoint invocation pattern** and the data format your model expects

In Project 2, you will redeploy your model(s) as tools for your LangChain agent and present the data requirements to a partner team. You need to understand your model well enough that someone who has never seen your code can learn what data it expects and what the predictions mean.

---

## Constraints

- **Free Tier:** Use `ml.m5.xlarge` for training and inference. Deploy **one endpoint at a time** -- delete before deploying the next.
- **Region:** Stay in a single AWS region (e.g., `us-east-1`) for all resources.
- **Algorithm:** SageMaker built-in XGBoost for the primary model. Use scikit-learn locally for baselines.
- **Reproducibility:** Use `random_state=42` for all splits and any local model training.

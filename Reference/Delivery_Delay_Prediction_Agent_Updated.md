#                    **Delivery Delay Prediction Agent (O2C)** {#delivery-delay-prediction-agent-(o2c)}

##                                        **Veterinary Food Supplier** {#veterinary-food-supplier}

[Delivery Delay Prediction Agent (O2C)	1](#delivery-delay-prediction-agent-\(o2c\))

[Veterinary Food Supplier	1](#veterinary-food-supplier)

[Master Architecture & Design Document	1](#master-architecture-&-design-document)

[1\. Executive Summary & Purpose	1](#1.-executive-summary-&-purpose)

[2\. End-to-End Architecture Overview (The 5 Phases)	2](#2.-end-to-end-architecture-overview-\(the-5-phases\))

[3\. Key Data Sources	2](#3.-key-data-sources)

[4\. AI Capabilities & Integration Flow	4](#4.-ai-capabilities-&-integration-flow)

[5\. Key Metrics, Features, & Business Dimensions	6](#5.-key-metrics,-features,-&-business-dimensions)

[6\. Phase-by-Phase Architecture Explanation	7](#6.-phase-by-phase-architecture-explanation)

[Phase 1: Data Sources (The Raw Materials)	8](#phase-1:-data-sources-\(the-raw-materials\))

[Phase 2: Celonis Ingestion & Unified Data Pool (The Plumbing)	8](#phase-2:-celonis-ingestion-&-unified-data-pool-\(the-plumbing\))

[Phase 3: The Dual AI Engine (The Specialized Brains)	9](#phase-3:-the-dual-ai-engine-\(the-specialized-brains\))

[Phase 4: Agentic Orchestration & LLM Synthesis (The Cognitive Core)	9](#phase-4:-agentic-orchestration-&-llm-synthesis-\(the-cognitive-core\))

[Phase 5: Execution & Automation (Closing the Loop)	9](#phase-5:-execution-&-automation-\(closing-the-loop\))

[7\. Table Structure & Key Fields (Vet Food Supplier Copilot)	10](#7.-table-structure-&-key-fields-\(vet-food-supplier-copilot\))

[8\. The Table Relationships (Data Model Joins)	13](#8.-the-table-relationships-\(data-model-joins\))

[9.Clinic SLA (Scenarios)	14](#9.clinic-sla-\(scenarios\))

[10.Vendor Contaract Scenarios:	16](#10.vendor-contaract-scenarios:)

[11\. Quality Assurance (Scenarios)	19](#11.-quality-assurance-\(scenarios\))

[12\. History Resolution Logs (ServiceNow / Jira Tickets)	20](#12.-history-resolution-logs-\(servicenow-/-jira-tickets\))

## 

## **Master Architecture & Design Document** {#master-architecture-&-design-document}

![][image1]

## **1\. Executive Summary & Purpose** {#1.-executive-summary-&-purpose}

The Delivery Risk & Resolution Copilot is an AI-powered agentic workflow operating within the Celonis Execution Management System (EMS). It combines predictive machine learning, enterprise RAG knowledge, SLA intelligence, and historical resolution learning to predict logistics delays, quantify financial impact, and autonomously execute corrective actions.

The primary purpose of this Copilot is to transition the Order-to-Cash (O2C) logistics function from a reactive state (responding to customer complaints and paying late penalties) to a proactive state (resolving bottlenecks before the cargo is delayed).

Core Objectives:

* Predict: Forecast accurate ETAs and the probability of delay before or during transit.  
* Quantify Risk: Calculate the exact financial penalty at risk by cross-referencing predicted delays with specific customer Service Level Agreements (SLAs).  
* Retrieve Context: Search internal company policies and vendor contracts to determine legally and operationally permissible workarounds (e.g., Force Majeure exceptions).  
* Execute Mitigation: Trigger automated workflows to reroute freight, alert planners, and proactively notify customers.

## **2\. End-to-End Architecture Overview (The 5 Phases)** {#2.-end-to-end-architecture-overview-(the-5-phases)}

Unlike traditional linear pipelines, this architecture utilizes a modern Dual-Engine approach, governed by an Agentic Orchestrator.

* Phase 1: Data Sources & Ingestion: Pulls structured data (Oracle EBS tables, telematics) and unstructured data (weather feeds, PDF contracts, SOPs).  
* Phase 2: Celonis Data Integration & Data Pool: Harmonizes the data into a unified Order-to-Cash Event Log, creating the base object-centric data model.  
* Phase 3: Dual AI Engine:  
  * *Engine A (Predictive ML):* Runs inside the Celonis ML Workbench using XGBoost/LightGBM to engineer features and mathematically predict the delay and root cause.  
  * *Engine B (RAG Knowledge Base):* Uses ChromaDB/Qdrant to vectorize and store enterprise documents for semantic retrieval.  
* Phase 4: Agentic Orchestration & LLM Reasoning: LangGraph orchestrates the workflow, querying both engines. An LLM (e.g., Llama-3 70B or GPT-4o) synthesizes the math and the rules into a final business decision.  
* Phase 5: Action Flows: Celonis automatically executes the LLM’s recommendation via MS Teams alerts, email notifications, and Oracle write-backs.

## **3\. Key Data Sources** {#3.-key-data-sources}

To achieve dual-engine reasoning, the agent relies on a fusion of structured ERP data, live API feeds, and unstructured enterprise documents.

**3.1 Structured Transactional Data (Core Logistics & Materials)**

* Source System: SAP ECC or SAP S/4HANA (Simulated for POC)  
* Key Tables Ingested:  
  * VBAK & VBAP (Sales Orders): Customer IDs, requested delivery dates, and order quantities.  
  * LIKP & LIPS (Deliveries): Freight weights, routing, and physical delivery destinations.  
  * VTTK & VTTP (Shipments): Carrier assignments and transportation modes (Road FTL/LTL).  
  * MARA (Material Master): Extracts critical product flags (e.g., Shelf\_Life\_Days, Specialty\_Diet\_Flag for critical renal or gastrointestinal diets).  
  * KNVV (Customer Master Sales Data): Identifies the receiving veterinary clinic's operating hours and dock receiving restrictions.  
  * KNA1 (Customer Master General) & LFA1 (Vendor Master): Extracts the actual Text Name of the clinic and carrier required for the RAG engine to accurately search for policies.


  


**3.2 Contextual & Route Data (External APIs & Milestones)**

* *This data feeds the ML Workbench to detect immediate physical threats to the delivery schedule. For the POC, expensive live GPS is substituted with static route logic.*  
* Source Systems: External API Gateways & Route Geography  
* Extraction Method: Python Scripts via ML Workbench (Utilizing GitHub libraries like pyowm).  
* Key Feeds:  
  * *Live Weather & Storm Alerts:* Open Weather API. Provides localized severe weather warnings (snow, floods, hurricanes) intersecting with the destination ZIP code (vital for predicting road transit delays).  
  * *Static Route Geography & Milestones :* Instead of live GPS telematics, the ML model calculates the total route distance (Origin ZIP to Dest ZIP) and tracks "Time Elapsed" since the SAP Shipped milestone to calculate the predicted ETA.  
    

**3.3 Enterprise Knowledge Base (Unstructured Data for RAG)**

* *These documents are vectorized into Chroma DB. They provide the Lang Graph orchestrator with strict clinic compliance and financial rules required to handle vet food disruptions safely.*  
* Source Systems: Internal Quality Management Systems (QMS), SharePoint, and ITSM tools.  
* Extraction Method: Python scripts parsing and embedding text into a Vector Database (ChromaDB) via Celonis ML Workbench.  
* Key Document Types & Rules:  
  * *Clinic SLAs & Vendor Contracts (DocuSign CLM/Ariba):* Defines specific delivery window constraints (e.g., "Deliveries arriving after 5:00 PM will be rejected, requiring a next-day redelivery fee of $150").  
      
  * *Quality Assurance (QA) & Packaging Policies (Confluence/SharePoint):* Internal rules dictating cargo integrity (e.g., "If standard dry food transit is delayed \>5 days due to extreme weather, cargo must be inspected for moisture or pest damage before clinic delivery").  
  * *Historical Resolution Logs (ServiceNow/Jira):* Past planner notes detailing how to quickly resolve stock-outs for critical prescription diets (e.g., rush-shipping a replacement pallet via expedited courier to a clinic).  
  


## **4\. AI Capabilities & Integration Flow** {#4.-ai-capabilities-&-integration-flow}

The Copilot operates on a continuous "Sense, Think, Act" loop. Each AI technology is deeply integrated, where the output of one component becomes the critical input for the next.

**Step 1: Predictive ML (Sensing the Risk)**

* The Technology: XGBoost, LightGBM, and Feature Engineering running on structured data via the Celonis ML Workbench.  
* How it works: Continuously monitors SAP transactional tables (e.g., VTTK for trucks, LIKP for deliveries) and live API telematics. It cross-references the destination ZIP code (LFZIN) with the OpenWeather API to spot disruptions like Level 4/5 blizzards.  
* The Output: Generates a *Predicted ETA*, a *Delay Probability (%)*, and the *Probable Cause* (e.g., "52-hour transit delay due to catastrophic weather").

**Step 2: Agentic Orchestration & RAG (Gathering the Rules)**

* The Technology: LangGraph (Orchestrator) and ChromaDB (Vector Database).  
* How it works: Triggered by the ML prediction, the Agentic Orchestrator pulls the SAP Master Data Context (Customer Tier from KNVV, Specialty Diet Flag from MARA, Carrier Name from LFA1). It then directs the RAG Engine to search the Vector Database for the specific Carrier Master Vendor Agreement (MVA) that applies to that exact scenario.  
* The Output: Extracts specific *SLA Penalty Clauses* (e.g., $500 Platinum Clinic Penalty), *QA Inspection Rules* (e.g., Moisture Exposure), and *Carrier Liability Waivers* (e.g., Force Majeure).

**Step 3: LLM Reasoning (The Synthesizer)**

* The Technology: Large Language Models (e.g., Llama 3.1 70B for dense legal reasoning).  
* How it works: The LLM acts as the "Brain". It receives a consolidated JSON package containing both the ML Prediction (Math: "52 hours late") and the RAG Output (Rules: "Carrier is FedEx; Product is a Critical Prescription Diet; Clause mandates $1,000 Air Freight mitigation").  
* The Output: The LLM weighs the facts and generates a *Financial Risk Calculation* and a *Recommended Action Plan* (e.g., "Weather verified. Void Force Majeure due to Telematics Disconnect. Apply $200 Penalty and authorize Air Freight").

**Step 4: Celonis Action Flows (The Executor)**

* The Technology: Celonis Automation & Integration modules.  
* How it works: Action Flows ingest the LLM’s final recommendation payload in structured JSON format.  
* The Output: Bridges the AI with the physical business by pushing approval alerts to Logistics Planners in MS Teams, drafting early-warning emails to destination Veterinary Clinics, and executing API write-backs to SAP (e.g., automatically posting a $500 debit memo chargeback to the carrier’s LFA1 Accounts Payable ledger and updating the VDATU delivery date).

## **5\. Key Metrics, Features, & Business Dimensions** {#5.-key-metrics,-features,-&-business-dimensions}

To operate effectively, the architecture tracks three distinct layers of data: KPIs, Engineered ML Features, and RAG Contract Dimensions.

**5.1** **Key Business Metrics (KPIs)**

* On-Time Delivery (OTD) Rate: Percentage of shipments arriving on or before the promised date.  
* Customer SLA Compliance %: Percentage of deliveries meeting specific timeframe SLAs.  
* Total Penalty at Risk ($): Financial value of potential late fees across active shipments.  
* Order Cycle Time: Total time from Order Creation to Final Delivery.  
* Automation Rate: Percentage of delay alerts resolved automatically without human intervention.  
  


**5.2 Critical ML Engineered Features (The Predictive Drivers)**

* Route Distance Remaining (Miles/KM): Calculated via live telematics.  
* Current Stage Duration (Hours): Time stuck in the current process step.  
* Weather Severity Index (1–5 Scale): Normalized score from API precipitation/wind data.  
* Port / Border Congestion Score: Live index of wait-time multipliers.  
* Transportation Mode Risk Weight: Risk multipliers for Air, Ocean, or Road based on seasonality.


**5.3 RAG Contract & Policy Dimensions (The Reasoning Rules)**

* SLA Target Window (Days/Hours): Exact allowed transit time.  
* Grace Period Threshold: Buffer time allowed before financial penalties apply.  
* Daily Penalty Rate ($): Invoice deduction/fine incurred per day of delay.  
* Force Majeure Clauses (Yes/No): Liability rules for delays caused by extreme weather or acts of God.  
* SOP Escalation Approvals: Thresholds dictating if a planner can autonomously upgrade to premium freight.

## **6\. Phase-by-Phase Architecture Explanation** {#6.-phase-by-phase-architecture-explanation}

To fully understand how the Copilot operates autonomously, the architecture is broken down into five distinct phases, moving from raw data extraction to automated physical execution.  
![][image2]

#### **Phase 1: Data Sources (The Raw Materials)** {#phase-1:-data-sources-(the-raw-materials)}

Before the AI can make decisions, it must collect all relevant variables. This phase is divided into three streams:

* Structured ERP Data: The foundational ground truth. Oracle EBS provides the baseline schedule (when was it ordered, where is it going, who is carrying it).  
* Contextual APIs: The real-time physical reality. Since Oracle doesn't know if it's snowing, external APIs provide live telemetry (GPS) and environmental hazards.  
* Unstructured Docs: The business rules. Contracts and SOPs dictate the legal and financial boundaries the company must operate within.

#### **Phase 2: Celonis Ingestion & Unified Data Pool (The Plumbing)** {#phase-2:-celonis-ingestion-&-unified-data-pool-(the-plumbing)}

Raw data is useless if it isn't connected. This phase acts as the enterprise nervous system.

* Data Integration: Celonis securely extracts data from Oracle (via RFC) and external systems (via Webhooks).  
* Unified Data Model: Celonis acts as a massive relational database, linking a weather alert for a specific coordinate directly to the Oracle TRIP\_ID that is scheduled to pass through that location.

#### **Phase 3: The Dual AI Engine (The Specialized Brains)** {#phase-3:-the-dual-ai-engine-(the-specialized-brains)}

This is where the architecture advances beyond standard AI by splitting tasks into two specialized engines that run in parallel.

* Engine A (Predictive ML): This is the Math Brain. Running inside the Celonis ML Workbench, it uses algorithms like XGBoost to look at historical patterns and live features. It doesn't know about contracts; it only knows that based on the math (weather \+ distance \+ carrier history), the truck will be 3 days late.  
* Engine B (RAG Knowledge Base): This is the Legal/Policy Brain. Using ChromaDB, it searches through thousands of vectorized company documents. It doesn't know the truck is late, but it *does* know that for this specific customer, a 3-day delay costs $5,000 unless a weather exception applies.


#### **Phase 4: Agentic Orchestration & LLM Synthesis (The Cognitive Core)** {#phase-4:-agentic-orchestration-&-llm-synthesis-(the-cognitive-core)}

This phase mimics a human logistics director managing two specialized analysts.

* LangGraph (Orchestrator): Acts as the project manager. When a shipment is at risk, LangGraph asks Engine A for the ETA, and simultaneously asks Engine B for the SLA rules regarding that shipment.  
* LLM Reasoning Engine: Acts as the executive decision-maker. It takes the output from both engines and synthesizes them using natural language processing. It calculates the exact financial risk and formulates a legally compliant, cost-optimized mitigation strategy.

#### **Phase 5: Execution & Automation (Closing the Loop)** {#phase-5:-execution-&-automation-(closing-the-loop)}

An AI recommendation is only valuable if it is implemented. This final phase bridges the digital AI with the physical supply chain.

* Celonis Action Flows: Triggered by the LLM's structured output, this orchestration layer executes the recommendation. It handles the manual, tedious work: pinging the planner on MS Teams for approval, writing the new carrier assignment back into Oracle EBS, and keeping the customer informed via automated emails.

## **7\. Table Structure & Key Fields (Vet Food Supplier Copilot)** {#7.-table-structure-&-key-fields-(vet-food-supplier-copilot)}

**1\. Sales Order Tables (The Baseline Demand)**

* VBAK (Sales Document Header)  
  * VBELN (Sales Document): Primary Key.  
  * KUNNR (Sold-to Party): The Customer (Clinic) ID. *Critical for linking to the KNVV tier to query the Vector DB for specific Clinic SLAs.*  
  * VDATU (Requested Delivery Date): The baseline target date to measure "delay" against.  
  * ERDAT (Creation Date): Used to calculate total Order Cycle Time.  
  * AUART (Sales Document Type): Differentiates STANDARD orders from RUSH/expedited clinic orders.  
  * NETWR (Net Order Value) & WAERK (Currency): *Crucial for the RAG engine.* If cargo is condemned or delayed, the LLM reads this field to calculate the exact 100% or 150% financial chargeback to the carrier.  
* VBAP (Sales Document Item)  
  * VBELN (Sales Document): Foreign Key to VBAK.  
  * POSNR (Item Number): Primary Key for the item level.  
  * MATNR (Material Number): What exact vet food product is being shipped.  
  * WERKS (Plant): The originating warehouse.  
  * KWMENG (Order Quantity): ML uses this to check for volume-induced capacity constraints (e.g., massive pallet orders vs. single bags).

**2\. Delivery Tables (The Physical Goods)**

* LIKP (Delivery Document Header)  
  * VBELN (Delivery Number): Primary Key.  
  * KUNNR (Ship-to Party): The physical destination clinic ID.  
  * VSTEL (Shipping Point): Exact loading dock/facility.  
  * LFZIN (Delivery Destination ZIP Code): *Critical for the AI Copilot to map against the OpenWeather API to detect intersecting Level 4/5 blizzards.*  
  * WADAT (Planned Goods Issue Date): When it was *supposed* to leave the warehouse.  
* **LIPS (Delivery Document Item)**  
  * VBELN (Delivery Number): Foreign Key to LIKP.  
  * POSNR (Delivery Item): Primary Key for the item level.  
  * VGBEL (Reference Document): The associated Sales Order (VBAK-VBELN).  
  * BRGEW (Gross Weight): *Crucial ML feature. Heavy LTL shipments take longer and face different route restrictions.*  
  * VRKME (Delivery Unit): Defines if it is shipping by Bag (BAG), Case (CS), or Pallet (PAL).

**3\. Transportation & Shipment Tables (The Movement)**

* VTTK (Shipment Header)  
  * TKNUM (Shipment Number): Primary Key. The overarching ID for the truck.  
  * LIFNR (Carrier/Vendor ID): *Critical for querying ChromaDB to pull the exact Master Vendor Agreement (MVA) for that specific Carrier.*  
  * VSART (Shipping Type): Mode of transport (Road FTL, Road LTL). *Massive ML feature weight.*  
  * STATUS (Overall Status): E.g., Planned, In Transit, Delayed.  
  * DPABF (Planned Departure Date): The ML model calculates "Time Elapsed" by tracking live telematics against this departure timestamp.  
* VTTP (Shipment Item / The Bridge Table)  
  * TKNUM (Shipment Number): Foreign Key to VTTK.  
  * TPNUM (Item Number): Sequence in the shipment.  
  * VBELN (Delivery Number): Foreign Key to LIKP. *This is the critical bridge connecting the physical Truck (*VTTK*) to the actual Clinic Deliveries (*LIKP*).*

**4\. Master Data Tables (The Identifiers & Constraints)**

* KNA1 (Customer Master \- General)  
  * KUNNR (Customer Number): Primary Key.  
  * NAME1 (Name 1): Translates IDs into text (e.g., "Banfield Pet Hospital") for LLM prompt context and SLA retrieval.  
  * ORT01 (City), REGIO (State/Region), PSTLZ (Postal Code): Used to map exact geocoordinates for the Weather API.  
* KNVV (Customer Master \- Sales Data)  
  * KUNNR (Customer Number): Primary Key.  
  * CUSTOMER\_TIER: Custom flag (e.g., "Platinum", "Independent") instructing the LLM to apply strict $500 penalty matrices.  
  * CLOSE\_TIME: Custom field (e.g., "17:00"). *Crucial for the LLM to calculate "After-Hours Arrivals" and mandate that the carrier absorbs Redelivery Fees.*  
* LFA1 (Vendor/Carrier Master)  
  * LIFNR (Account Number of Vendor): Primary Key (Maps to VTTK).  
  * NAME1 (Name 1): Translates IDs to text (e.g., "FedEx Freight") so the RAG engine can locate Carrier Exception policies.  
  * STRAS & TELF1: Carrier address and dispatch contact information for automated Copilot email alerting.  
* MARA (Material Master \- General Data)  
  * MATNR (Material Number): Primary Key.  
  * MAKTX (Material Description): Identifies the exact diet (e.g., "Feline Renal Support").  
  * SHELF\_LIFE\_MOS (Minimum Shelf Life): Identifies QA limits for dry food. If transit delays breach this, the LLM forces the Carrier to pay for Bio-Secure Destruction.  
  * SPECIALTY\_DIET\_FLAG (TRUE/FALSE): Custom flag to elevate alert priority. If delayed \>48 hours, this flag triggers the RAG engine to authorize emergency Air Freight replacement at the carrier's expense.

## **8\. The Table Relationships (Data Model Joins)** {#8.-the-table-relationships-(data-model-joins)}

To create the flattened event log and feature tables for the ML and RAG engines, your Data Engineers will need to configure these exact SQL joins inside the Celonis Data Pool. These joins ensure the LLM has a complete picture of the truck, the pallets, the clinical rules, and the carrier contracts.

1\. Order to Delivery Join (The Fulfillment Link):

* LIPS.VGBEL \= VBAK.VBELN (Links the physical delivery item back to the original sales order header to calculate total cycle time and delays against VDATU).

2\. Delivery to Shipment Join (The Physical Bridge):

* VTTP.VBELN \= LIKP.VBELN (Links the specific delivery pallets to the shipment bridge).  
* VTTK.TKNUM \= VTTP.TKNUM (Links the bridge to the actual physical truck/trailer).

3\. Shipment to Stages Join (Excluded for POC):

* *Note for Architecture:* In a full SAP environment, VTTK joins to VTTS to track individual route legs. For this POC, we have intentionally excluded VTTS to keep the Machine Learning model lean, relying directly on VTTK-DPABF (Planned Departure) and live API telematics for ETA calculations.

4\. Transaction to Master Data Joins (Context & RAG Triggers):

* Customer Location: VBAK.KUNNR \= KNA1.KUNNR  
  * *RAG Purpose:* Pulls the clinic's physical ZIP code (PSTLZ) so the Copilot can ping the OpenWeather API for blizzards on the route.  
* Customer SLA Rules: VBAK.KUNNR \= KNVV.KUNNR  
  * *RAG Purpose:* Pulls the CUSTOMER\_TIER (e.g., Platinum) and CLOSE\_TIME (e.g., 17:00). Crucial for the LLM to apply the $500 delay penalty or authorize overnight holds.  
* Veterinary Product Details: VBAP.MATNR \= MARA.MATNR  
  * *RAG Purpose:* Pulls the SPECIALTY\_DIET\_FLAG and SHELF\_LIFE\_MOS. Crucial for the LLM to know if it must authorize an emergency Air Freight replacement for a delayed critical diet.  
* Carrier Identity & Contracts: VTTK.LIFNR \= LFA1.LIFNR  
  * *RAG Purpose:* Translates the vendor ID into the text string (e.g., "FedEx Freight") so the RAG engine can search ChromaDB and retrieve the exact Master Vendor Agreement (MVA) associated with that specific 3PL carrier.


  

## **9.Clinic SLA (Scenarios)** {#9.clinic-sla-(scenarios)}

* Scenario 1: "Platinum Clinic Delay. Shipment arrives past the SAP Promised Delivery Date (PDD) grace period of 24 hours. Platinum tier clinics (like Banfield and VCA) impose a strict $500 flat penalty per day of delay, automatically deducted from the invoice."  
* Scenario 2: "Independent/Gold Clinic Delay. Shipment arrives past the 24-hour grace period for independent vet clinics. Independent clinics incur a daily penalty equal to 5% of the total invoice value, capped at a maximum of 25% of the total order value."  
* Scenario 3: "After-Hours Arrival (Receiving Window Violation). The ML predicted ETA falls after the clinic's operating hours (extracted from SAP KNVV), meaning the truck will arrive when the clinic is closed. The delivery will be rejected, and the carrier must return the next day, incurring a $150 redelivery fee and adding \+1 day to the SLA delay penalty. The AI Copilot must proactively instruct the driver to hold at the depot and not attempt delivery to avoid the $150 fee."  
* Scenario 4: "Extreme Delay Cancellation. A standard vet food shipment is delayed for more than 7 calendar days past the original PDD. The clinic reserves the right to outright cancel the order. The Enterprise absorbs a 100% revenue loss, plus return freight costs from the carrier."  
* Scenario 5: "Expedited/Rush Order Failure. An order flagged in SAP as a Rush Order fails to deliver within 48 hours. Standard grace periods do not apply. The carrier forfeits the original freight charge, and the enterprise must issue a 10% discount on the food invoice to the clinic."  
* Scenario 6: "Prescription Diet Stock-Out Risk. The delayed material is flagged in the SAP MARA table as a Specialty Diet (e.g., critical renal or gastrointestinal support food) and the delay is \>48 hours. Animal health is at risk. Logistics Planners are auto-authorized by the AI Copilot to spend up to $1,000 to rush-ship a replacement pallet via expedited LTL or air courier to prevent a clinic stock-out."  
* Scenario 7: "Minimum Shelf-Life Reject. Due to severe transit delays or warehouse mismanagement, the product will arrive at the clinic with less than 6 months of remaining shelf life (based on SAP MHDRZ). The clinic will reject the food as 'short-dated.' The entire shipment must be recalled, returned, and destroyed safely."  
* Scenario 8: "Pest/Moisture Exposure QA Hold. Transit time for dry kibble exceeds 6 days due to carrier breakdowns or extreme weather, leaving the trailer exposed to high humidity and elements. The shipment must be placed on a strict QA Hold. It cannot be delivered to the clinic until a local quality inspector verifies the packaging has not suffered moisture or pest damage."  
* Scenario 9: "Severe Weather Exemption. The OpenWeather API indicates a Level 4 or 5 weather event (e.g., Blizzard, Hurricane, Flooding) intersecting the destination ZIP code. This constitutes an Act of God. All standard SLA financial penalties are fully waived."  
* Scenario 10: "The 12-Hour Notification Rule for Weather. A Level 4/5 weather event occurs, but the enterprise must notify the clinic. To successfully claim the Force Majeure waiver, the AI Copilot MUST trigger an automated email notification to the clinic at least 12 hours before the original Promised Delivery Date. Failure to notify reinstates all financial penalties."  
* Scenario 11: "Mandatory Mode Shift (Road to Rail). Cross-country blizzards impact FTL (Full Truckload) shipments for \>48 hours. The Carrier is contractually mandated to shift the freight to an intermodal Rail network to bypass the road closure. The Carrier cannot mark up the base contracted rate for this emergency shift."  
* Scenario 12: "Carrier-Caused Delay. The delay is caused by a carrier truck breakdown or a lack of driver availability (No weather exemption applies). The 3PL Carrier assumes 100% financial liability for all clinic SLA penalties. The Enterprise passes the cost directly to the carrier's monthly invoice via chargeback."  
* Scenario 13: "Emergency Cross-Docking. A carrier's truck breaks down in transit and cannot be repaired within 24 hours. To protect the integrity of the veterinary food from extreme temperature fluctuations in a dead trailer, the carrier must cross-dock the freight to a secure, climate-monitored warehouse within 24 hours at their own expense."  
* Scenario 14: "Copilot Auto-Approval Threshold. The ML Delay Probability is \>85% and the Revenue at Risk is \>$500. The Agentic Copilot is authorized to automatically approve expedited routing costs up to $500 USD without human intervention to save the SLA."  
* Scenario 15: "Director Manual Approval Threshold. Mitigating a delay requires a freight upgrade costing more than $500 USD. The AI Copilot cannot auto-approve this. It must generate and route an actionable approval card to the Regional Logistics Director via MS Teams. The SLA requires the Director to click approve or reject within 2 hours."


## **10.Vendor Contaract Scenarios:** {#10.vendor-contaract-scenarios:}

* Scenario 1: Standard Transit Delay (Carrier Fault). The carrier (LFA1) fails to deliver the shipment (VTTK) within the contracted transit days due to poor routing or driver shortages. The carrier is subject to a 10% deduction of the base freight rate for every 24 hours delayed, capped at 50% of the total freight bill.  
* Scenario 2: Origin No-Show / Tender Rejection. The carrier accepts the freight tender but fails to provide a truck at the originating SAP warehouse (WERKS) within 24 hours of the Planned Departure Date (DPABF). The Enterprise will re-broker the freight, and the original carrier is liable for a $350 "Truck Order Not Used" (TONU) penalty.  
* Scenario 3: High-Value / Rush Freight Failure. A shipment is flagged as an expedited rush order for a critical medical diet. The carrier guarantees 48-hour delivery. If the carrier misses this window by even 1 hour, they forfeit 100% of the freight invoice and must reimburse the Enterprise for any SLA penalties levied by the receiving clinic.  
* Scenario 4: Carrier-Caused Medical Stock-Out. The carrier delays a critical prescription diet (MARA Specialty Flag \= True) by more than 48 hours, forcing the Enterprise AI Copilot to rush-ship a replacement via Air Freight. The original LTL carrier is legally liable to pay the cost difference between their standard rate and the emergency Air Freight invoice.  
* Scenario 5: Emergency Cross-Docking Mandate. A carrier's truck suffers a catastrophic breakdown in transit. To prevent the veterinary food from spoiling or suffering extreme temperature fluctuations, the carrier must independently cross-dock the freight to a secure, climate-controlled warehouse within 24 hours entirely at the carrier's expense.  
* Scenario 6: Pest/Moisture Exposure (Trailer Integrity). The carrier's dry van trailer develops a leak or is left open during a multi-day transit delay, exposing the dry kibble to high humidity or pests. The carrier is held 100% liable for the wholesale value of the cargo if the destination QA inspector marks the shipment as "Condemned."  
* Scenario 7: Short-Dated Product Delay. The carrier delays a shipment so long that the product arrives at the clinic with less than the minimum required shelf life (SHELF\_LIFE\_MOS). Because the carrier's delay caused the product to become "short-dated" and rejected by the clinic, the carrier must pay for the return shipping and destruction of the food.  
* Scenario 8: Severe Weather Liability Waiver. The Copilot's OpenWeather API detects a Level 4 or 5 weather event (e.g., Blizzard, Hurricane) intersecting the carrier's active GPS route. This grants the carrier "Force Majeure" status. The carrier is fully exempt from all delay-related financial chargebacks for a period of 72 hours.  
* Scenario 9: Telematics Disconnect Penalty. The carrier contractually agrees to provide continuous API GPS tracking (e.g., FourKites/project44). If the carrier’s truck stops transmitting GPS signals for more than 12 consecutive hours during transit, the AI Copilot automatically voids any weather exemptions and applies a $200 blind-tracking penalty.  
* Scenario 10: Weather-Mandated Mode Shift. In the event of an API-verified cross-country blizzard closing major highways for \>48 hours, the FTL carrier is mandated to immediately shift the trailer to an intermodal Rail network. The carrier must absorb any drayage costs and cannot mark up the base contracted freight rate.  
* Scenario 11: After-Hours Arrival (Redelivery Fee Assumption). The carrier arrives at the veterinary clinic at 6:30 PM, but the clinic's dock closed at 5:00 PM (KNVV Close Time). The clinic rejects the truck. The carrier must hold the freight overnight and redeliver the next morning, but the carrier *waives their right* to charge the Enterprise a standard $150 redelivery fee because the late arrival was the carrier's fault.  
* Scenario 12: Missing Equipment (Liftgate/Pallet Jack). The carrier arrives at a small independent vet clinic that does not have a loading dock. Despite the delivery being coded for "Liftgate Required," the carrier shows up in a standard 53-foot trailer. The carrier must return with the correct equipment and absorbs a $250 service failure penalty.  
* Scenario 13: Dumped / Unattended Freight. The carrier driver unloads the pallets of vet food in the clinic parking lot or outside the back door without getting a physical signature (Proof of Delivery) from the clinic staff. If the food is stolen or ruined by rain, the carrier is liable for 150% of the cargo value.  
* Scenario 14: Rail Yard Demurrage Liability. For intermodal shipments, the carrier is granted 48 hours of "Free Time" to pick up the container from the destination rail yard once it arrives. If the carrier fails to dispatch a driver within 48 hours, the carrier is solely responsible for paying all daily Demurrage storage fees (typically $150/day) charged by the rail yard.  
* Scenario 15: AI Auto-Deduction Agreement. The carrier legally agrees that the Enterprise's AI Copilot is the authorized system of record. If the Copilot calculates a delay and applies a $500 penalty based on API timestamps, that amount is automatically deducted from the carrier's monthly accounts payable statement. The carrier has 14 days to dispute the Copilot's calculation via an official portal.

## **11\. Quality Assurance (Scenarios)** {#11.-quality-assurance-(scenarios)}

1\. Thermal Degradation (Extreme Heat): If OpenWeather API registers \>100°F intersecting a stationary truck (VTTK) for \>24 hours, critical care diets (MARA-SPECIALTY\_DIET\_FLAG=TRUE) must be placed on QA Hold for vitamin degradation testing.  
2\. Freezing / Canned Food Burst Risk: If ambient temps drop below 32°F for \>12 hours, canned/wet diets must be visually inspected at the destination clinic (KNA1) for bulging seams before dispensing.  
3\. Trailer Leak / Moisture Exposure: If telematics cross-reference heavy precipitation and the clinic rejects the load for "wet pallets," the cargo is deemed a biological mycotoxin hazard and is strictly Condemned.  
4\. Double-Stacking Crush Damage: SAP LIPS-BRGEW (Weight) mandates "Do Not Double Stack." If the carrier violates this and bags are crushed, the carrier is 100% liable for the invoice value (VBAK-NETWR).  
5\. Pest Intrusion (LTL Terminal Dwell): If a shipment dwells at a third-party LTL terminal for \>72 hours, pallets must undergo black-light inspection for rodent/pest intrusion prior to final-mile delivery.  
6\. Short-Dated Expiration Breach: If a transit delay causes the remaining product life to fall below MARA-SHELF\_LIFE\_MOS, the Copilot must auto-abort the delivery and mandate a return to the origin plant (WERKS).  
7\. Tampering / Broken Security Seal: If the physical trailer seal does not match the SAP Bill of Lading upon arrival, the freight is strictly embargoed. Global Security must be alerted immediately.  
8\. Odor / Chemical Cross-Contamination: If LTL freight arrives smelling of chemicals (fertilizer/tires), the palatability is ruined. Freight must be placed on QA Hold for sensory/lab testing.  
9\. Shock / Vibration Kibble Pulverization: If telematics indicate a severe collision or hard-braking event, Dental Specialty diets must be shake-tested to ensure kibble hasn't been pulverized into useless dust.  
10\. Dumped Freight (Ground Exposure): If freight is left outside without a signature, bottom-layer bags are automatically Condemned due to ground moisture and pest exposure risks.  
11\. Condensation / Sweating Swings: If the truck transits through a rapid 40°F temperature shift within 12 hours, clinics must be alerted to check shrink-wrap for internal condensation/mold.  
12\. Emergency Cross-Dock Puncture Risk: If a carrier suffers a breakdown and cross-docks freight, any bags punctured by third-party forklifts must be isolated and Condemned due to oxygen exposure.  
13\. Unapproved Transloading (Lost Custody): If a carrier transfers freight to an unvetted sub-contractor without Enterprise approval, the freight is Condemned due to a broken bio-security chain of custody.  
14\. Lab Quarantine Release Protocol: Freight on QA Hold cannot be commercialized until a certified Enterprise Inspector updates the SAP Delivery block (VBAK-LIFSK) status to "CLEARED."  
15\. Bio-Secure Destruction Rule: Condemned veterinary food must NEVER be sent to a standard landfill. It must undergo certified bio-secure incineration to prevent gray-market diversion, funded by the liable carrier.

## **12\. History Resolution Logs (ServiceNow / Jira Tickets)** {#12.-history-resolution-logs-(servicenow-/-jira-tickets)}

*(Format: IT Service Management Tickets. The LLM reads these to learn how to solve problems autonomously).*

TICKET 1: INC-26-001 (Medical Stock-Out Mitigation)

* SAP Refs: VBAK-8000102, LFA1-C901, MARA-SPECIALTY\_DIET\_FLAG=TRUE  
* Resolution: Carrier delayed \>48 hours. Planner bypassed carrier, cut a new SAP rush order, and deployed Emergency Air Freight. Logged $1,450 debit memo to Carrier C-901 for mitigation costs.


TICKET 2: INC-26-002 (Blizzard Mode Shift)

* SAP Refs: VTTK-TK10400, LFA1-C902  
* Resolution: OpenWeather flagged Level 5 Blizzard on I-80. Planner mandated Road-to-Rail mode shift. Rejected carrier's $600 drayage invoice markup per MVA Addendum 021\.

TICKET 3: INC-26-003 (Missing Liftgate Redelivery)

* SAP Refs: LIKP-9000455 (Liftgate Req), KNVV-TIER\=Independent  
* Resolution: Carrier arrived in 53' dry van without liftgate. Clinic rejected. Planner ordered cross-dock to straight-truck. Levied $250 Service Failure Penalty.

TICKET 4: INC-26-004 (Telematics Disconnect)

* SAP Refs: VTTK-TK10550, LFA1-C904  
* Resolution: Carrier GPS dropped for 14 hours. Planner voided all weather exemptions and manually posted $200 Blind-Tracking Penalty to Carrier AP ledger.

TICKET 5: INC-26-005 (After-Hours Arrival)

* SAP Refs: KNVV-CLOSE\_TIME\=17:00, Arrival=18:30  
* Resolution: Carrier arrived late. Clinic closed. Planner forced carrier to hold overnight on refrigerated trailer. Waived standard $150 redelivery fee due to carrier fault.

TICKET 6: INC-26-006 (Origin No-Show / TONU)

* SAP Refs: VTTK-DPABF\=2026-08-15, VBAP-WERKS\=PL01  
* Resolution: Carrier accepted tender but failed to spot equipment at Plant 01 within 24h. Planner re-brokered freight and charged original carrier $350 TONU fee.

TICKET 7: INC-26-007 (Dumped Freight / No Signature)

* SAP Refs: VBAK-NETWR\=$4,000, LFA1-C905  
* Resolution: Driver left 2 pallets in alleyway; rained on overnight. No POD signature. Planner Condemned cargo and charged carrier 150% of invoice value ($6,000).


TICKET 8: INC-26-008 (Rail Yard Demurrage)

* SAP Refs: VSART\=Rail, Free Time Expired  
* Resolution: Carrier failed to retrieve container from Chicago rail ramp within 48h. Planner rejected carrier invoice attempting to pass through $450 demurrage.

TICKET 9: INC-26-009 (Short-Dated Rejection)

* SAP Refs: MARA-SHELF\_LIFE\_MOS\=6  
* Resolution: Extreme delay caused product to arrive with 5 months shelf life. Clinic rejected. Planner mandated return to plant and charged carrier $500 Bio-Destruction fee.

TICKET 10: INC-26-010 (Hurricane Force Majeure)

* SAP Refs: VTTK-TK10899, OpenWeather=Category 4  
* Resolution: Hurricane intersected route. Carrier parked safely. Planner verified via API and granted 72-hour liability waiver. Zero delay penalties applied.

TICKET 11: INC-26-011 (Thermal QA Hold \- Heatwave)

* SAP Refs: OpenWeather=105°F, Dwell=48h  
* Resolution: Truck broke down in Texas heat. Planner placed freight on QA Hold. Directed carrier to nearest cold-storage cross-dock. Cargo ultimately Condemned.

TICKET 12: INC-26-012 (Broken Security Seal)

* SAP Refs: LIKP-9000500  
* Resolution: Seal cut before clinic arrival. Planner immediately embargoed delivery. Initiated theft/tampering investigation. Charged carrier 100% cargo value.

TICKET 13: INC-26-013 (Double-Stacked Crushed Pallet)

* SAP Refs: LIPS-BRGEW (Do Not Stack)  
* Resolution: Clinic reported crushed bottom layer. Carrier stacked heavy pallets on top. Planner issued credit memo to clinic, charged carrier for exact damaged item (VBAP-NETPR).


TICKET 14: INC-26-014 (Rush Freight Failure)

* SAP Refs: AUART\=RUSH, Transit\>48h  
* Resolution: Carrier guaranteed 48h delivery but took 50 hours. Planner completely zeroed out the freight invoice (paid $0) and passed clinic SLA fine to carrier.

TICKET 15: INC-26-015 (Chemical Cross-Contamination)

* SAP Refs: VTTK-VSART\=Road (LTL)  
* Resolution: Kibble arrived smelling like industrial solvent. Planner rejected load, mandated lab testing. Product Condemned. Carrier account placed on compliance block.

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAaMAAAJACAYAAAAgrQlFAABnJElEQVR4Xuy9CbQc133eieMce0bwOc6cmfCcTCxgHC/JSewAdjST402C5YwjOV4Qx4ss2oFtSSZlDWLJkm3FBiVbNuXAEkXtAklREMRF4L6AJAguIEgQ3ASAJEAQ+3vYH97DDjxsxMI77yvoa/z7X1X9qruru6q6vu+d71T1rbtV1b33V7equt+U0EKbNm0KGzduDJs3bw5Dw8NheHiHLMuyLCd6y5YtETPggwcPhnY0xQdAx44dizI7dfpMOPvGOVmWZVluy7v37Ik4cu7cOY+YRMVgdAlCp2MZy7Isy3K7PnTo8MSsadijJqYmGAFEPiNZlmVZ7sY7d+6MbuG1UgNGApEsy7LcK58+fSaMjY1Z/jQpghGeEenWnCzLstxLY9KTpghGmhXJsizL/fDRo0c9hyJNwevbemtOlmVZ7ofTZkdTNCuS8/Dv/f7vhylTpkQ+dPhIeP6FFyNj29vf8Y5w7333R+vYjrhMd+2nPx2F8TPzgJmenjp1aqxcn4ZhSJuWL8pHXna7LWPatGmNz6i3rTPqi/1jnlhPKh/7jM87d+1KLN+G+TogzO8r8sE+Ia3N06ZJ+uzrwLJZP5aVlBbriM/jYc+bLHdqMOfixYueRWEKvtDqI8tyu7YDFQayJBhh4ObgbuPaJeL6vDGYctDEZwyOhJtNa9cR94UXX2qKZyGDdfuZxn4AOByEsc46IK80GOEz1rHdxmEZto4wjw8hw3CW44+DhZE9Zjw2Nh6WHhysh80X9eRnnjObF46hLc/nKcudeHRsLIyOjnoWhSn4ZQUfWZbbtZ0ZYZ0DG20HcgsBXpVzQLZpfBl+tkDbuH7w9wDCktBAnTh427yYFku7naBKghGNzx4kNt+kfU2KayEKWxjBLNcCxedh8+f5sMfQw8jnhTCWh3DBSM7DR48dC7sm2rPXlOHhHbHIstyu/UCVNDOyAyQHWwuPtIGczgIj5mPLIlDs7IDbLKw4K8GSt+v8zIgzPFuuX1pgvfWtb43V0cfxs0osUbYNtzBiPO6bzZvHyJ8PxrH19zBKmxkRRn4fZLkTA0b43pGXYCTnYj/4JcHIwoTrHFTtgE772UGr23Q0yvIDPQdcP2viOuPavPyg79PAPj/O/pLS+TpaYNrbdBaUMEHqYYQl87ZpLFxs/ozPNLCHkc8LZRJGNo4sd2PBSJZlWS7cgpEsy7JcuAUjWZZluXALRrIsy3LhFoxkWZblwi0YybIsy4VbMJJlWZYLd+4w2j86Gt71rneFoaEhn6dUAi1fvnzi/Lw7dt6KMtuLVE6Vrb389V//tdpLidVNe8kVRg8/sjS8973v9XlJJdTb3va22Pnrt9VeqqOytJe0X3aWyqWPfOQjsfM3mXOFkRpKtVT0AKP2Ui0V2V4wI1J7qZbabS+5wQgklKqlW2+9NaxevSZ2LvthtZfqqcj2oltz1RPaiz+PrZwbjH7913/d5yFVQO1eveRltZdqqqj2IlVTmzZviZ3LNOcGo+uvv97nIVVARQ0uai/VVFHtRaqmvrloUexcpjk3GN14440+D6kCKmpwUXuppopqL1I19dWvfS12LtMsGNVcRQ0uai/VVFHtRaqmagujWbNmNZYw/s8Nlvh/K/Pnzw9r1qxp/AfR6dOnN/4/C4Rts2fPbsTHcmRkpLEO4fOcOXO+W1qI1sfHxxtlQczPxkVZLA/1wBLlMW6RKmpwKUN78cK5hCl7jnCOcQ6XLFkShSGe3YbzmtSm2N6QDqbYvhAHabmd+SOvMqqo9lIW8bxwOW/evOj8QThvHDPQ9+Err7wyaiuMb/v+ypUrG9tw3hGf6SHkizC2G6SD0HbY/jg2Md+yjCtUbWHEgQAnFLKAIIx4QjkI2IGDjYogYQOyMGIZbAxMz7KYxsII22wj8w2zSBU1uJShvXj5c8HzxrbA84Z4WMc2tBlejCS1KQ4OFkZYMl+mIZwIo7KqqPZSFnkY4dzZcw9xLMC55AUO4mM7xyZeyFoYwTYt1m27YftE2ldeeSVaR542X4KqLKotjHDS7InhieUMCScTJ5JgYkPCybONCfmggXCwsDDyMyNevbAsyg82WGc+yBvxsfQDYL9V1OBShvaSJLYBnBecI7YVnDsLI16xctDguUxqU3awgexFiW13EOPZdlYmFdVeyiL2aZ5DCw2IfZvbIF6I2vbA88ttPO+ECdsf2xnEsYJlI61tQ1j3ba1o1RZGUvsqanBRe6mmimovUjUlGEmZVdTgovZSTRXVXqRqSjCSMquowUXtpZoqqr1I1ZRgJGVWUYOL2ks1VVR7kaopwUjKrKIGF7WXaqqo9iJVU4KRlFlFDS5qL9VUUe1FqqYEIymzihpc1F6qqaLai1RNCUZSZhU1uKi9VFNFtRepmhpIGPGLrBC+5DVt2rSmL4xB/GUE/jpC0he/+KW1JPGLaPaLj/zMbQjjN+Uhu+6/qMjPM2fObHxhkmIZdr9Qb+wXxXXkw29V+zK6VVGDS6/bSzvil5F5jOfOnds4zmhHOEc4h/aLzfjpKAhpEdd+kZVfcMbPvdgvzjLOjBkzGvmg7bCdoRx+ORtLbkOeLJ/tCGXYL072S0W1l36KfZNfPrXnhV9w5TjCL5miPWDJc8yxiOcR4rlDv7ZjENZxfpnOjhXYxrisj5UdD9gmy6TKw+iKK67wQU1gQWOxg7Y94dC2bdsa4ZD9eQycdA4M/mdX7DedCTrG4UlHXnabj2fFcH4zGuu2TijPDiRYR2NHPJTHdXYO+83tvFTU4JJne8mqhQsXRvbiQEDhGOOYsz3wYsJeQBAUCLO/oMD4iMN2Zy9GEG7PIePY9sS2wQEQQnu3F0lsR5Avv5cqqr30QmgLSWONPbYWRjYc4ljCfsyLDiwJIp8G59gCBiLIIA8bhrF92O286PZjVJk0kDCCfAdnI7Cd1s4i7JWs7chJJxzigMF0jMcrIQhlcTCCuI4y/aDANH5mxLTMC7KDDsV1m9bPsLpVUYNLnu0lq9JgxPPB88WLB54brONc8fxyZmNnR4jLtoD249uqhZFtJ0wH2YsT5Il82C6Qh23DqCvLtxdivVZR7aUXSoMRzwHhwgsDjjkULw5t/+f4AiMNTNn+zPNqxxK2I9s+/GzIjkmQZkYJLmJwkbpXUYNLmduLv6jopco4gLRSUe2lrmpnttPPi5KsEoykzCpqcFF7qaaKai9SNTWwMEp7NuNlnxFBdhrMJe/D2mmwvwrhrRVeKbN8PJNCnszXX5HwWQ9vpyTVG1N+Tts5rbfx7D1i+3DTb+9WRQ0u/WgvWeWf56XJthPE9e3Fy557m/dk6Si2O9+ei1RR7aWfsv2ylVrdMse5a9U/J8vbP8ek7HMiPlucTGyHvr6+DNQ5a9vMqoGEEe/jQjiR7bxNx87MA41bIzwx9s0WfyJwsjCI2Hv1FMKRD+rg09m34Pw2is8A+KDTi+kQzzeaPAenogaXXreXdmQ7KTsuzjXOLc4NnxkgjHHx2V4Y4JzgIsQ+p2R7YXtgPJTBiw8IeSFfpkW4fZGFzyP4TILx+nk7kSqqvfRTPK44L2wPPG/slxzc2TY45kD+ORDbCs4d2xPSLlu2rJEH0+LcMj7HN4rPpiis+3/uhzhob8yD+2DTM0+OLfhMeKKOeY4vlYeRPQGUvQLAgbOzBRxw2zExc0G4zWft2rXRQV6xYkUTVOzDRA8OlpEEI4ShTknA4eDT6kqDeWN70tUNwrFfkIcRlUejKWpwybO9ZBUeVic9sLYwsufawojbCAJ2cnZi5EF78U04xuMAZwcothMOQBwgoNHR0cY6tlsg9ltFtZdeCG0haayBCBSeC/Q1fLYvMfBiFeeQb/BC2G4vnhnftims23GHZbBP2/GNsuMA47JOEMdCtgvW3Y5BbDscQ20bYhtLGo86VeVhlDRgQDiR9mTxpPPkQryShOxVqn8DKunNFg8O3yAsjFgXpLEND2LeKN/nSTHvpMELYjrsWxqMfLmdqKjBJc/2klVpb9PZc8D2AKN94fjbwQTCeUc4zhHD2AZtR2Y75Ozbgodlsv1aGCEdtnNwYHkIs4NhES8/FNVeeqG0t+kg9nkcd54TDvw8rzgfnMn4C0NsQzqcQ7ahNBghLvNAGNoCykFahkF2LPF1wpLtBIaYl03H8RHbkmBky8tDlYdRkcLJ4RVFO2Iae3KroKIGl0FpL62UdiFSZRXVXqRL8tDLW3m3WcFIyqyiBhe1l2qqqPYiVVMDCyN7m66VfBxOO3m7C0t77z9pGkzxdgq3YSqLenAKbLdBnJozHszbKrZMe3+WcdNu2fVSRQ0u/WgvWeXfamxH7can7C2+PG639ktFtZd+yvb1yeTvhKTdUrdKGmdaCfHt2NGJ7LOifmogYWTvxeOA8tvpME4QOzTve0L2mRG3QTi59llRnjBC2fYWH2GE+Kwj4rMuWPLZRBEqanDpdXtpR3wOgGcwOE984YD3z3F+CA+s8zPEtsP2ifbi2wPOrW2jDLftz5Zj24L93Cn48lRR7aWf8n2d/RPmeUY4nxcRQDinWIdxrvCZ58+OX8yf7QHb+XYwxxaOD8zHjleIizDmb8tn+0R6jl0IxwtczBdpOCaxfD5/zLuNVR5GSc9rbEfGAeNDO4T7k23fbKHwCiS0YMGC6OTwZLPhQFlghAboYWTFerBhsDHzM4T62isU+7MuBGm/VNTgkmd7yaq0t+nQBvj7YDivOOc8FzxvONdct+fIw8ifW8T1YZTt+MzXvrhAcbCxbbwoFdVeeqG0t+lsX/fn234maJJgxHPFtmTHL38hA7j4sYSfmY8dr7iN7RH5cFyzZaFuFMch5INwjoFIx21Q3m2s8jBKk32xgFez+MzGgHUOIFi3ndq+PQfhBCIOwQL5BgF5GNmrl6T4ENJwVmZPNMuE/ICD8LT8eqmiBpd+tJesQvthx8U5wjo7aRKMcG55fj2McO45MECEEdLbgQ/p/FUo2y/bBtJwMIPsoFiUimov/ZTt6xDvwuA8cDzg+MILDcThxYQfjzyM7DjGMcjOZJgOwpJthXGRn80bQlrbPjmTYjksH+VwfIQ4LlJ5t7FCYPT+97/f5yFVQEUNLmov1VRR7UWqplY991zsXKY5NxihkUrV0/s/8IHYueyH1V6qqaLay/Lly31VpArIn8dWzg1GJ8ZP+jykkquoq1xY7aV6KrK9vOtd7/bVkUqudttLbjCCP/KRj4TFixf7vKQSCrfJ/Pnrt9VeqqOytBepGmoXRHCuMILxwOrWW2/1+UklEhrKq+vWx85dEVZ7Kb/K1F5QF7WXcqsTEMG5w8j6m4sWRYNN1X3VVVfFwqrodh4m9tubNm8ZmPbyZx/9aCysilZ76b0/8clPRvbhVXS37aWnMBoUA0Y+TJbT/JnPfDYWJstJvv/+ByL78Do6FUZbtmyJRa6rBSO5HQtGclYLRpd98OChsG/fPs+iMGXjxo2xyHW1YCS3Y8FIzmrB6LIxKzp+/LhnkWBkLRjJ7VgwkrNaMLpsMCdJUw4ePBh279kTS1BHC0ZyOxaM5KwWjC578+bNnkORoh8u0uzokgUjuR0LRnJWC0aXvHdv/FkRFcHo3Llz4dChw7GEdbNgJLdjwUjOasHoktNu0UGNnxceHh6OHiz5xHWyYCS3Y8FIzmrBqDWIoMu/dT8hvOZ9+vSZWCZ1sWAkt2PBSM7qusMIIBodHbW4iakJRtDY2FhtnyEJRnI7FozkrK4rjPCMaLIZERWDEXX06NEok4hoE4DCt2YH3YCRD5PlNOMfmPkwWU7yXXffHdmHD5rxhVY87gE30t6aS1MqjKiLFy9G06tdu3ZFhQyyASMfJstpvvbaa2Nhspxk/Ogr7MMHzfhlhaQvtGbRpDCqkwAjScqq6667zgdJUqLwb8L5r8OlZAlGRoKR1I4EIymrBKPJJRgZCUZSOxKMpKwSjCaXYGQkGEntSDCSsgr/6fjxxx/3wZKRYGQkGEntSDCSsurDH/7wpN+zqbsEI6M//dM/DYsWLfLBkpQowUjKKl3oTi7ByOkrX/lK+PjHPx4eeeQRv0mSmiQYSa20d+/ecM899whEGSUYJWj16tVh4cKFUSOSZe+//du/jdoJYeS3yzL8yU9+Mtx77712aJFaSDCSpA6EweZjH/tY+OhHP+o3SZLUgQQjSepQAJIkSflIMJKkDnX11Vf7IEmSOpRgJEkd6oMf/KAPkiSpQwlGktShBCNJyk+CkSR1KMFIkvKTYCRJHUowkqT8JBhJUocSjCQpPwlGktShBCNJyk+CkSR1KMFIkvJTrjA6di6EXafeDDtOXpTlgffVEzDyYbI8iN53+k0/3OeujmH02P4L4VMbzkV+cN+F8PLRixGIZLkuBox8mCwPqneefDO8cOhC+Nq2842x/8wFT4bO1TaMHtx7CUL37L4Qq6ws18mCkVxnbxl/swGlPJQZRgKQLDdbMJLlS3724MWIEbtPdX47b1IYfWvH+fDAXt2Ck2VvwUiWm/2dw5eg1IlawgiZ3rJTsyFZTrJgJMvJBjvwQls7SoURMvMFyLJ82YKRLKf71p3nw/DJ7LftEmH0xOjF8MIh3ZqT5VYWjGS5tTGpOXA2G5BiMPrHTXhVWyCS5cksGMny5L5u83mPmUTFYPSFredjmcmD49VD+8KUKVMafnjV6vCWqVOjbRvHToRv3P1gtI4wbGe637xyTiMNPvs8GI/pmKc303C7zed//P3/jJaoB+OjPnY702A/WHeEo342P1vmv5g2vbGNYT4+jLLsftp0sE/zgQ98IPz022dFRp1tXizD1tnWifG43YbbOmIfWQ/sKz4jDpc06o56IK4N9/F8WTY9whgfx9fvE7exPjTPOfOx54xl2rySzoc82MYkZzI1wUjPiQbfGGQ48HCASYIRBgysIz4/28Gj1UDCgYfgYzgGSx/XQwvxLYx8mciTg5+HkS+P9lDBOuJj/2xZDPfpkcbXHZ85M8I664bPyJN1Qv04ONv0PJ4W5CyL6w0YvXVaVIaHkT12FkY8h7CNh/zs/tn0LJf1tcDhNuSVdIxt+yHMuY1tyIahnrzwsPnIg+snRy9MOkNqwOiBvRfCbTs0Kxp025kRBhd/5cwBmlfsdvDioOvT+DIQ5q/4YX9Fzbg065YGIwx6hBHyR139zIggtIO8hRHWGR9LxGca5GVnRnYf/L4mwcjW2wPSHyeGtYIR8rDnyMOIeRAgfmbE+ISFPU6whxGPg68H1wlkf26Rj91HmzYJYDz2NkwefE/2yncDRn+nWVEtbGdGsB2sODOyswA7SPGK2V/9WtsBzhtlcSBjvj4+w21+/MwymYYDLgdZzkCwj3bQ9beFsOR2hnEWY9PZOvm6eRjZY8I6My8/M+K2pAGZn5EGJowsZLm0xy7LzIjHhtsYjrogHWcsDLPH3YIKtm3En0N85nZ7fFmvpPzkevjePem/HxTB6MS5N8N6/bZcLZwFRnaQ4EwC6wj3t7xg5mdnARz4/IDDK3c70NF2VgLbAc3mYwdRCyOGJZXJfLDEPntQMI6tA8shNOwsxsPIxrMDOuP7OiFvH2bj2rqyXNaByzQYMb2ND1sQ2XLs8WEcLO15x3rSrTvYwwhmPWyZdr/sZzjpIkAePLeaHUUw0rMiWW7feptOltszfmA7TYKRLHdowUiW2/crRy96DkWasnjXhbDigH7yR5az+qqrrgpXX311ZKwPn9CLP7Kc1Wm36qZoViTL7Xno6NkIQrTfLstyugUjWc7RBNGnP/u52DZZltP9xa3nw/4z8Z8ImnLt64KRLHdizYpkuX0/PHI++v1Trylf2qL73fIlf+iJ/eF75q+TM/p7P/1yLExO9g9cvyHW3uR6euWBC+Gu3fG36qbcuF0wqruvfeFAeM8Du3zbkKRcdfOrhyMw+fYn18svHb4Q/dNWL8Go5n5h9Gw0QEhSP7T7+LloBu7boVwfC0ZyogUiqd9Cm9twVF8nqasFIznRb/nset8mJKmn+vTzY+Gqx0ZibVGuhwUjOdHv/PaQbxOS1FOt2DUefubWoVhblOthwUhOtGAk9VuCUb0tGMmJFoykfkswqrcFIznRgwgj/EuCOXPmNIXNmjUrjI+PN4VRCE/axn9v4DV37lwfFKZOneqDwvz5831QqtasWRO5nTRVlWBUbwtGcqIHDUZ+MF+yZEmYPn16A0bYDmPgRxggQhgBPBYqzIvpATik43JkZCQKh5gPwrFOsCBPxMM25EO4IQ+mRVxsYxqsIw1EsPLzIEgwqrcFIznRgwYjDOhWHMQJI0LEwsLOjOxMiDBCWoQTYoADjDQeRoSOBQvEdPwMSLIsDyPO6vDZljsoEozqbcFITvSgwQjCAE5IcJ0wAjT8zIUQAQTszMjepsO2GTNmNCDyyiuvRHEJFw8jzrRYBuNYGCFPbOP6smXLGjBiGsFIHjQLRnKiBxFGUrklGNXbgpGcaMFI6rcEo3pbMJITLRhJ/ZZgVG8LRnKiAaObbrpJlvvmVatWCUY1tmAkJ1ozI6nf0syo3haM5EQLRlK/JRjV24KRnGjBSOq3BKN6WzCSE+1hZL8X04n4HRn73Rqs8/s7/N4MxbjdlJlFLINfKE36zC+zJtWH3w/idn6vyH4xFmI6fqZYDsS80mTjtitbJ3y5N21f7C88eNk0Pr39zO8+IT+7T9hujwePLSUY1duCkZxoDyOKgwcHXQwoGOQ4wFEIswOvH0inTZvWWPcDtA/Dlz8h/mzOypUro6X9tQKWjzCktfWxMPFivbi0XyK1cIT8PqAcxuc2/sQP0zJ869atjV9bgFiX2bNnN9btzwJhnfvNQZtp+QXYpOOGuPzlBuaFzzNnzmyCEYUv1ELIC3FgxJ83b160ZF5WqJcFjhfysOcX6/Yz5I87JBjV24KRnOjJYAQRRv4KmOEcGCGmY7x2YARxBoV0/IkexEEZGFx9+fhMKHAQRlympSxEoKRfNPD7QHEf+UsJlIUR1lesWBGto76sG4+bhSA+Y4n8+Pt2rBcBxONmQUwhLY4T4vF4WJgkwYifkR8gwiV/3SEJRlArGCGPLDDiRQwlGNXbgpGcaA8jwsFCAoMOB1eG21mMHWz8oG8HJ26zeXsYoRwOxgQKZ2d24Gad8JlX8LYerB/lIWlhxG1+luNloQJZGEGY/UAM4xJ1JGR5HFE+0/tt9hhy/yxcsR3pPYwQl8eB6a0IaUAIQr48Zlh66EFpgObxJVStIX8sLcwEo3pbMJIT7WE0SLrmmmt8UK3lwV+UBKN6WzCSEz3IMJLKKcGo3haM5EQLRsniW4D+9pTUvQSjelswkhMtGCWLz7rsMyEpHwlG9bZgJCf6527Z5tuEFJJnRljnA3r/sJ9vqCVtk5r1+I7x8I7bBaO6WjCSE/0989f5NiGF5LcALYwg/8pyq23SZX1w2d5wzaqxWFuU62HBSE70Dy3YFG5+9bBvF5LUM+ECyLdDuT4WjORUa3Yk9UuffelAuHPreKwNyvWxYCS3NIAE37flWPSAWZbzMp4R4dYc2pdAJAtG8qTecPRCeNddO6I3neTJ/U8/vyEWJseNlxX0jEimBSNZztkYaH2YLMutLRjJcs4WjGS5fQtGspyT37ZoW7QEjF4+dC588eXDsTiyLCdbMJLlnHz92sONFz70mrIst2fBSJZzNEH0wzdsim2TZTndgpEs5+ih8YuaFclyBxaMZLmFd5y8OAGYN8OmYxfC+iPno2dBL429EZ7ffzY8s+9seGrvmbBs9+nwyM5T4YGhk+He7SfD3CdHwr3bxsOS4ZNh2a7T4fGJ7Ssm4j07cja8OJF29YE3wquHz0evzG+eyHf7iYuxcmW5bhaM5NIZg/23Nh4P175wMPzew3vDL96xI/zrGzeHK764oemZTCv/b5/fEH5kwaYw8xtbwjtv3x5+9e4dYc7Du8NHntwX5j2zP3zupQPhxlcOhbs3HQuPDp0IL46cChsOng37xs+F42cvhDPn3wznL77p+0VPhfJOT5Q7MlGHrUfOhpcm6vTUzvFw7+Zj4VuvHQlfWH0wXPvcaPjY8pFw9bI94Xce2BX+813D4Wdv2RZmTOznW7+yMXYc0vx9n1kf/s8vb4xeuvidB3eHj67YH77+2rGwdAKqO07Gz4ks99qCkdwXY2ZwCS57ot+9+96JwdAPkDQGVQyyH3ps7wQwDoelE7DYcPBMGD15zrdTqUOdmwAfwPvCvlPhm+uPhL9dNRr+y707wr9fuDX8k4RzQk+9bn34uduGwl89OxZu2XQ8DI9rVifnY8FI7tjrjpwPf/HMaPiZW7c3DVg/8LnXwttv2x4+NTHA3b/lWDh57qJvX9IA6dWx0+G6iZnmf3toV/jnX3o9BjDMvv7hxYOx9iPL1oKRnMl4zoFbOXaQwa2wj68YCct3jvv2I0kNPbvnZPjjR/c0tZ2ZC7eFR3eeirUzub4WjORUv3PxcDRw/MZ9O337kKRchOd1BBReEvFtUK6PBSM50Rgc/n7VqG8XktQzoc19bs2hWFuU62HBSE40BobZ9+zw7UKSeqJVe05GbU6/61dfC0Zyot/57aGoIeA2Cl4b5q2UP39qJKw7cMY1F0nKLrzs8BM3X25TX56YDUH4H0eCUX0tGMmJJoy8PvzEvvB/fOHy933wKvCfPTkSXhk97aNKUli0/nD4o0eaX1743Qd3hUe2n/BRBaOaWzCSE50Go1Y6e+FiuGvTsXDlkl3hX924uWkAov/Xz66P8r7q0b3hG+sOh2d2n5xI198vl0rtafvRN8KyiRkyXtX//Ylz+2M3bIqdV/rX7tkR/m4iXiezZ8Go3haM5ER3AqMswq8bPLljPCx4+VB0xfz2W7eF/+WzyV+A/f7rXgs/OTHzetedw+H/e2xvuPa5sXDHxqPRoLV3XF+AbVenz18M68ZOh8eHT4SvTRz/T6zcH947MUv5D4u2hWktfr3hhxdsCr90x1C45pn90Uxn46GzPutcJBjV24KRnOhewShPYXAdPvZG9D0nfLn2668ejn7m56+e3h/mPr4vvOeBndEvOfyHRVvDv7kJPycU/0JmVT11AuD/19c2hp/4+uboXP3a3Tsm4L47/OWKkegtyBteORxu33AkPDYBntX7T4VjExcBZZdgVG8LRnKiqwAjabAkGNXbgpGcaMFI6rcEo3pbMJITLRhJ/ZZgVG8LRnKiBSOp3xKM6m3BSE60YCT1W4JRvS0YyYkWjKR+SzCqtwUjOdGCkdRvCUb1tmAkJ1owkvotwajeFozkRAtGUr8lGNXbgpGcaMFI6rcEo3pbMJITPYgwmjNnThgZGYmWU6ZMCVOnTo3CscRneNasWVEY1sfHx6NtDGNcaM2aNU1h9jM1ffr0aInyIOSJ8rFEfKSbP39+tA3h06ZNi9ZZhq+PDWc+gyTBqN4WjORE1wFGEKGAMKxj8Cc8sA5YIA1FIABUMAToECpWhBG3IV8aYtkQykB5S5YsidKxTKRlvS28EEcwkgfJgpGc6EGEEQZzDPZwKxhhO6GFQR+fKYIE4YCRBQLSI52FFMT8mSfLAlg8jJAf0yGM5TMu0iF/xh0kCUb1tmAkJ3oQYSSVW4JRvS0YyYkWjKR+SzCqtwUjOdGCkdRvCUb1tmAkJ1owkvotwajeFozkRANGR44ckeW+WjCqrwUjOdGaGUn9lmZG9bZgJCdaMJL6LcGo3haM5EQLRlK/JRjV24KRnGjBSOq3BKN6WzCSEy0YSf2WYFRvC0ZyogUjqd8SjOptwUhOtGAk9VuCUb0tGMmJFoykfkswqrcFIznRgpHUbwlG9bZgJCeaMOK/OMC/LLD/1ydNSf/Xh8K/PsD2VnGSxH8wR6Wl9/Wz//ohq/jvG7ikWuXl64d6+LqkicfEi/+qIovwbyX4z/18vfNUlrx5nJKOF/+1RpoEo3pbMJIT7WEE8X/92P8HNHv27MY6tuMzxP9mirj8PzwzZ85swAjbYf5PIP6zOv8/evAZ6biN/+GUn+2gzf//Y7czDzsQ2rph3cKA8RDG/xtk/6eR/a+uSMs8bDorxGcaHBvUl/8wD/u1cuXK6LP/Z3l2v5in/X9IENIgby4ZZsU8kYbHD+J+rVixogFTbEcY4vLiw6bjcWCe9pzyM4X/WovPPDaoH8HL8pDWxhGM6m3BSE60v02HgcgOZDNmzIg+8x/KwQQVBxgMZBzEOUj6mRGhwcGUoICYlvkQHEyPz/xX3RAHTM4UkIYDH8tPqpvNw8MI4r5ZiNorf5RBoHgYMT7rZGGBdQ7QfiZlYcR/xkcQEw4Q0jJvyOcPsX6QPYcQ6w3xeLJswMKuE0YQ94X1ZxhFGEHMf3R0tOl4sC48noJRvS0YyYn2MyMsOXhgnVfOdlDBoINwDGAYpOyAj3DEJUzsoEmIcODjkjBgeRDTc6CzM7ckGMGsC5RUNwsj1svCi3EJJV7lMx7rRiEetxPOk8HIA8nCiPsF2eMLtYIR8+TxRpo0GDE/ghr5sSzG9zBCGCFNcTv3G8J25A8jD9aLdYOQl2BUbwtGcqL9zKjusjOhKsoCbDJZENp1L8yWLHS6lWBUbwtGcqIFI6nfEozqbcFITvT3zF8XTp676NuFlCI+C4GpvGYMddFPf2tbuOqxkVhblOthwUhO9bc3n4igBF/30oFw4g3ByT4n8c+KeEsLb81hG2A0d+7cBqCwzHqrrA769utHoxk42teP3rg51v7kelkwkjN5ziN7w/d+Zn0DTu+6cyh8bgJQp2o2e+ILAPalBsq/gMEXCwAgvkxRVz29azy898Fd4Z99cUOjDb37rh3hlo3HYm1NrqcFI7lrL95yIvzKPTvDD1x/eaCB/8mEf2rhlvCXK0bCbRuOhtGT8YZWNfk3B62SYIQZFGdSgJJPU1XhFu5ze0+GT60aDb95387wT925h6d9dWP4q5VjYenOU7E2I8vegpHcMw+ffDM8suPUxIA0Gv7LfbvCFV98PTZg0f/u5i3hV+/eEeY9sz/c9Mqh8OK+UwMFryro1bHTYcm24+HvJgDz/qV7wv+zaOvEOYtDBv7+z70W3rZoW/jw8tFww7qjYcNRjRdydxaM5FL7OwfeCA8OnwwLJga8a188GP7k8ZHwngd3h5+7bSj8ywWbwg9MDIp+oMxiXMn/4Fc2hp/4+ubw09/aGn75zuHw2/fvDFcv2xM+tnwk/I+J2dw1E2DEwPwPz49Fz8y+uPpg+Orag+Hrrx4O31x/JNz++tFw56Zj4b4tx8KSrcfDsqET4ckdl35J4ImJ5SPbj4f7J7bds/lY9HzklteOhJsn0t7w8qHwpYm8Pv+dg+EfXzwQPj2R/988OxqBGLPIDz22N8x5aPcEnIfDO2/fHmZ+Y0v40Rs2hf/9CxvC95lbpe34rV/dFGZ8Y2t49wTwf++hPeEvnxkN//idQ+H2zSfCsyNnw46T8WMvy/20YCTX0huPXQirJ0D3xJ7T4YGhk+GWTcejK/z5Lx0Kn1g1Fv7q2bHwFxMD9keeGg3//cn94erHRsL7Ht0b/mDpvnDlxGAOIP709T8ffv3eneGX794Z/tNdO8I7Fw+Ht98+FH721qHwjonlf7xjx8TgvzO6hYmZ4W89sDu8dyLtf3tkb3jfsn3hjx/bFz40Adc/ncj/Yyv2R4CYN1Hupyeg+4WXD4dFrx8Pd249EZbtOh0B47WJ2cfQ+MXYvsjyIFgwkuUODRj5MFmWO7NgJMsdWjCS5fwsGMlyhxaMZDk/C0ay3KEFI1nOz4KRLHdowUiW87NgJMsdWjCS5fycCqMbBCNZbmnBSJbz8wuHLoRbkmA0f+O5WGRZli9bMJLl/Lxs5HxYOnLBsyhM+dQGwUiWW1kwkuX8fNvErOiVo/EfXhaMZHkSC0aynJ/BnCRFMNqp36uS5VQLRrKcn1NhtPH4xXDj9guxBLIsX7JgJMv5+aah+MsLUPSvKXWrTpbTLRjJcr5OUgSje/doZiTLaRaMZDkff/r15Ft0UAQj6OkDApIsJ1kwkuV8nPa8CGrASLfqZDnZgpEsd+9nDsRf57ZqwAjvfV+3WUCSZW/BSJa7d6tZEdSAEfTEqP67pCx7C0ay3J0BomOtWdQMIwiJMEvymclyXS0YyXLnvnP3hXD2YvIbdFYxGEF6fiTLly0YyXJnXjF2YdLbc1QijCABSZYvWTCS5fb9/MEL4aF98R9ETVMqjHZPZKZ/LyHLgpEst+tHR7LPiKhUGFHIED8Z5AuT5bpYMJLl7P70xkuTmHY1KYwgAOkbw/pSrFxPC0aynM1gxZrDrb9PlKZMMKJQkJ4lyXWzYCTL6X5s/6Vbci8d6gxCVFswgg6evUQ/eMMx3b6TB9+CkSzHfc+eSxD6VsK/EO9EbcPIC29MEE6yPIgGjHyYLNfVi3ZcCK8f724WlKSuYSRJgy7ASJKk3kowkqRJJBhJUu8lGEnSJBKMJKn3EowkaRIJRpLUewlGkjSJrn3sf/qgnurCa3f5IEkaeAlGktRCe4/tDSuHnvXBPdXp637IB0nSwEswkhqaPn16tJw1a1YjbGRkJMyfP7/xmUoKS9OcOXPC+Pi4D55Ua9asiZa+LIRzG2XrnJc+ev9fFHKL7syXfjycuqZ3XXPq1Kk+qCEeR5z3JKWFU0uWLPFBkpRJvWvxUl/16r514eo7PhTe8cV3RgNoJyaMMFhhHQM+YYRByg40BMSUKVOiONgG6MBIh+1YRz6EEfNCGopp4NHR0SiMA6KFEeoEWwixXMSnUY6tC9YJL9TF73Mr/+Ht72+U1W9d2LI0AlLehggjHD8cExzfGTNmRGEWRjhPOH48/jYNjjPbBYz1Vu0A9nXJ02e+9u/DG8v/JqqjVE0JRgMgDJxrd7/sg9uWnRlhHQOLhZGdoVgYIZ4dhJjGDkSEBJwGo5UrV0bxOCBa8DAtwwlKpvUw4iBKGCFuqxlBncTjgGODdRynefPmRWEWRpS9gCCMCBoedx7nJBjxXPRab545FoFJqqZ05iqu53e8EMFo0DXZ7SFJos7e9z4fJFVAglHF9dsLfzccPX3MB0tSbaXZUTWls1Zx1WFWJEntSDCqpnTWKi7BSJKaJRhVUzprFZdgJEnNEoyqKZ21ikswkqRmCUbVVNdn7c2Jv4e2PxJu37g48r1b7w+PDC0NS4celftgwMiHyXKdDRj5MLk3fmT40fDAtgcb4/8dm+4KGw9t8pjIpI5h9MaFNxoV2HJkaxg9NSYXYMDIh8lynQ0Y+TC5P951Ynd4atfTERdW7mnvZ7TahtHwsR1RQVuPbItVRO6/BSNZbrZgVB7fs+W+iBdZ1BaM7t5ybzQN8wXKxVkwkuVmC0bl8tB3JzDnLp7zSGlSJhideGM8yswXIhdvwUiWmy0YldPP7Hk2vH5oo8dLQ5lgBBDtGx+JZS4Xb8FIlpstGJXXrW7ZTQojzYjKbcFIlpstGJXbYMqeE3s9alrDCIk2Ht4cy0wujwUjWW62YFR+J82QUmGEt+Z2Hd8dy0QulwcJRo+vejz6VwXwLXffGoX9zNt/trFt3dD6aP0tU98SxWE6hOMz4uAz84CZBkaeNp3171z5O03pUAa3MU1avgxjXX9w2g/G0nJ9aGw4FsfbxmOeMPeTRhjrec3fX9N0rOw+YL+RH9MwH6Tx+Q2CBaNqeNmOx5uYkwoj3Z6rhgcNRhYoWCbByA+eWOcAa9N6IxwDcysQcFsSjAAsHx9mHZkmCUYo98f/3Y9HAPBxrH28JBjZ+NwnwoiAYRk4bhZGiGNhZPMfFAtG1TAYg++rUokwQgR9j6gaHjQYETQc2PmZwMGgikEUAyzhxFkNYWHT+DI4CPtw2sLI5+M/0xzQUTcPO5vWwiQNRthuZzFJMIJ5fLCd+8R1O2uDLYxQrmZGcllsb9clwmjJ9odiieRyetBgxJkR7WdGdgD1MxWEtboVB9uBPsndzIxQPw+jJKhiX5JglHQbLglGvmyU+e5ffXe0jvKQPwGNbRZGWHqA+XpU3YJRdbx0+NEGd2Iwwm/N6RZddVw3GNnBmIOrncVw0LUDv40PY6BGuAUO3QpGk+XLeHaGhwGfkLLbUA7jcBvCbDysJ8GIJlhYB7tOs2wLYZatmZFcBr92cEPEnhiM8KOn+q256niQYCTLeVgwqpZ5qy4GI82KqmXBSJabLRhVy4LRgFgwkuVmC0bV8uM7nwi7T+yOw+iOzfoh1CpZMJLlZgtG1fJLo6vD2tGX4zDCP8bzkeXyWjCS5WYLRtUyfuVn+a6n4jDCf+/zkeXyWjCS5WYLRtXypsNbwpM7lwtGVfVvfOO3w8ObljZg9Atf/n9jcWS5Th7/3L8Mh9bd1oDRyb/7/lgcuXwWjCrukZP7IxDRd7x6dyyOLNfKE30CIKIPfeer8Thy6SwYDYBvf3lxA0Z+myzX0Ydf+EIDRn6bXE4LRgNigOi/fuO3Y+GyXFcDROPX/3AsXC6nBx5Gu4/vCat2Phee3PbUQPtdC34lFjZofnpoZdh8aEvsHMvteezYrnBw+2Ph4Kb7B9on/+GfxcIG0WMHNsTOcRU9kDDaenhb47bV27/4zvCHt78/fOiu/y5X3B9Y/MHw7gno8tw+sW157NzLyR47uDGc+PrPR7OF03/zfeHM194Wzn7jF+SK+8zNs8LpCejyluSx+/4wdu6r4oGC0aeW/X14x5d+Mew7ts/vjjSg+pO75obfXPi7sbYgXzIGJwxSbx4Z8odOGlABUCeu/7FYWyi7BwJGO47tjK6UpfoKUMKLHL5t1NVjR4ciCEn1FaCEFzl82yirBwJGApEEoR189bkFsfZRR0ezoaM7/CGSaia0gyNPzou1jzK68jASiCSrm56/Oazd90qsndTJmhFJVueWfzIc2PN8rJ2UzZWG0X++4dfDbatv91WXaq46f9/q5Px/Hs49+xl/SKSaqwrft6o0jL70zFd8tSUpjI0fqC2Q3nj0Y/5wSFJ48/ie0gOpsjD6q4ev8VWWpIZ+9vPviLWZQffxO37HHwZJauj0J74n1mbK5MrCqGzPiqZOnRqmTJkSecmSJdFyZGQkzJo1K6xZs6ZpOzR9+vQo3H5GfMZhOMTwJNn44+PjfnOT5s+f74MipeWdJMSdM2dOYx+xD5OVW5Qe3/ZkrN0MsvvxrMi3Ny7T2i/aPdodP7PN+Hg+by+7DW0PQpls02yPMOph07Ge7Qp1TxLKzdLmbZ2xz2XQoY33xNpNWVxJGD2wYUmYe/eHfZULFRqubaBogAgjjLCE2CgtjNB52Jmx9EJa5oMybCdhJ7ODwbJly5o6NdfRcdl5bSfBcuXKlVEZTIN1DiK2ToQqts+cObPUMLryljmxtjOoPvTyN8PZhb/oD0HuYvuwn9E+2P5woQIRGGkwYn+wYjvj0pbFdeSLMtgP2Bd8vSi2c7ZRtl8sLcCQJ/sC4qLOtu62TozDdfYrG49xIXvxBlto2zrxmPVSJ74yI9Z2yuJKwggvLowc3++rXKg8jAibadOmNTqfnTFxOwGA9Ekwso0+6UqNDZqyEGEDJ4DYafxggHgMw/Z58+ZF4aiL7TQQ6oDOhW2IX2YY1em5EV5c6Mer3EntDW2M7ZcwQjwCww7Wtq15se0zDys7cEPsN8yP27H0bdvOjCy8WB7qxtkd9mX27NmNuLYP4IKN8Qgspk/qK1xHnqgT8mOfIZAm6995q8zPjSoJo7LdooN4dQOzcULsLHY7ZGHEhpl0mwMdk42ewLON1jZ+yObnGzsHBaZj3bDEbIqdmHnaAYRC2UiDbexYtqwyqU4w6sctOsi2T7Qz22aS2q+Fkb216+P5vPnZboPQb9guIeRFiDAt27hNx3paGNk0fhs/+z7A9aR+ZePZuIzDdd9nODYkQThvCUY5u4wwksonwUjqpSxcqiLBKGcLRlIWCUaS1CzBKGdXEUa4TcDbAl5p0/OkB5q8Xw0hT58W23ClxvvSra7a7O2MVsoar2wSjMot3rprpblz5/qghnhb0PcB/5m36LKI/SerUIcqSTDK2VWDUVKH4/MWNGY++OVzJj5ERRx0WNs50DnxmW/o+I6DvG6//fbGiwt4gQJLPnC19/nxGfnABBefZSE9wrCcMWNGYx+S9qWsEozKL3th5R/g+/bv4xA6aKds42y79jPbNNs42zzXLYBs+2a/gBEHn/kcCariRZpglLOrBiOAxT/ct/eb2QHY+CG8Ns3OZjsgAYF0Pk9oxYoV0dJ2RnZEhtsrR/sQl/VAHJRP2TQefmWWYFRe2RkFB3y2w7vuuquxDe2Nb7fxqwQUw9FuASqkZV72M/oBzLZOiNiXitj2mSfEN+Qs5Bg/qe9VQYJRzq4ijCA2ZMjOSLiNV18QZyYIt/CA0EkIOJsnxLicZaFTEl4Q0mEdr6kiHdbRORGPdcE6wrmd9apaBxSMyisLI4KAgz9k+wnbuZVv+2izbPtsz/ZiDuuEiZ0dIa7Nm3kiLvsZ84f45h77U9VmR4JRzq4ajOzUv8ryUCy7BCMpD6UBx95xqIoEo5xdNRhJxUgwkqRmCUY5WzCSskgwkqRmCUY5u5cwuummm+Q+u1cSjPKXP3dyvu61BKOc3UsYSYMjwUiSmiUY5WzBSMoiwUiSmiUY5WzBSMoiwUiSmiUY5eyiYMTvIPjvPFD+G+SQ/e4Qv6eD9PyOEdaT0nmlvVbN7zvwexCU/wyhLHxPwpfLuElpqizBqH+y3/vhd9y80r7iYL9fZL9snVVsz8w/qY9yG7/oyleybb9i+7dfrGVeSf0v7ZVviHnxC7NleQVcMMrZ/YQRGrHtRGxk9gup/HY3fyoEjc8Dho3ZNmrkgXT250Wwnd/25rr/1QTbCSyM7LfNUTcLFztA+HIXLFjQ2IdBkmDUe6Gd2S9Do02xDaJtot3xwotfNMU2O1hb2S+osh8xP6RheTDKws9dcaDnoG9hAtn+gvgMY1zkhXX2H5ve9iH2R66jbkyH+iIu88M6f4aI9WKfRtkcVxDX/upDryUY5eyiYYTGxSsmCx2s+/gQGiJhQKjYBmobLMwOjatE5Ikyk67gmA/D2OnYGWwnZPnseL5cds5BkmDUeyXBCG0L4Vi3/cNeAFEeRmjzdqBmW9+2bVsUZmdO7H9st9huYcRw218II0KS9bTrrWDEPAkViPvLi1HI9j/2MewP0qFsrNvj1C8JRjm7nzDyYuNkI0KjwjpkYcROaOHERs4ZFRooocb0hAY7OZZs2CzPdhamZ714JWk7A5eIZ2/TsVx8th1tUCQY9V+2rUG8cIMIIwsZyN+mszDigM11DyPkw/bMfmbbNmT7C2/TIYx1tWDBOn4qi7L9y8MIP1rMcpCv7d+Y7RA8HkZYYrtg1GzBaIBkO74kGEnlFGdhRUgwytmCkZRFgpEkNUswytlFwYhXNGlvC3Uj3g7wtzA4xe9UvHVgb1Ukyd+792L9+JzJyqfFZ96mTLsF0c0+ZZVg1F9N1i/srbEk+dtr3Yr1QVvjLTyrVnXhrb+s7dT3gbJKMMrZ/YSRfeZjXyJAQ7f3tf09YzR0fLbPjpCe96ftNogAwnY+7+HDWCyZhvVBPCwZxwKAQjjvTSNP+xIDH+BSjMMwXz+GI44dVFC+7+zIH2/oQYyHdPZhM5Z4mGzBm7cEo96LF1CQhRHW+Zltie0G55x9x55/2x4hpGEbRFq0F76AwDbs2zzy4HMltkt8ZrtDeTD7FJe27TMe27RNy+dA3Gf2S7xgkdQHyybBKGeXAUa8ikNDZadJghEaMBopZ1QIS7riYqdkZ4E4E+FVGsxOTGhBzN9fVRJ8ABLMOKyXjY88EJcPk7FuHxYjL3ZAu5/QvHnzmq4MCWjWnYMCAQrZffLHIi8JRr0Xzl8SjNB+4GXLlkWf0d4II16gJAl52bZh2yD/4STLJEQof1EEYTviIRzp0E9ZPsORzv4zSyvAz6aFk/aZnzv5nlQ/JRjl7H7CyMpfOXEwZsfhlR7i8Z/YWbDYjuavonwejIclAYFB38KI6bhEmK0jOhvBgHwIQgh58vtFjMcl43gYMZ0FJMS0jM8y7eCEfeJAwf3ycfKWYNRfsZ2yD9g2yv/SSoDYtk6xD3DdXxBhHfE5w7YwImBsO7PhEPJEHQg0xmN+tu+wfdsLL/Yfe2HG/iIYdW/BaMDE22NF6JprrvFBhUowKocwWPfyokPKLsEoZwtGUhYJRpLULMEoZxcFI07rk+55J4VRrbZJvZNg1F/xNpe99Qah/fN2V5I0a+qfBKOc3U8Y8f43ZJ/xoHOhE2E7n5kQVjYcaQkjdbr+SjDqvexzFfYPtPvR0dFoiTZPGLH9o58gLpZ8buifH0m9kWCUs/sJIyvCxsIJtjDiA03E4UNRvhgA822eVleKUj4SjPor+5ILxJcA2N75oJ8v5SA+YcQ3KhFHUOqdBKOcXRSMJpN9i0cqXoJRuaQ7A8VLMMrZZYWRVC4JRpLULMEoZwtGUhYJRpLULMEoZ5cVRvwyqBV/vqTVl+H87b2kfCDeS/fPm+xn3W+/LMGoXOIXWq3QXtF+0Qfsl04ZTnHdt/0k8cUhL75gkeXt1izlJJWBdPDatWtL2RcFo5xdVhhBHiKEEZbsDGisaKj8Jjc6ImBFYBFGCGentG8b+Y7Cz3w4LF2SYFQuJUHAAsoO7uwj9jOX9jcN0d7RrxBmXxRCXnyJyOfBdcSD8CyLb/chjEBhfbBEHIQxDvNHmSiD5aBeWLdfPvf9tUgJRjm7ijCC/JUSPxNGFjbIh52FM6fJYMQHxH57XSUYlUseRnYQ5+DOcLuEbJv2MxL0C7R9goKwQHm2z7F8hLFPoQwbjxeHhBE+czthBPn6sn74GTACiv9O3N/5KFKCUc4uO4xsJ0qCEX8eBQ2dv5EFGGGJz0jPqzU2coSzcSMMn3lVyTjsHHpr6ZIEo3KJMPC/ech2zDZtYcO+ZGGEfmLbOPoVjNkIL+L4GrkFAfsXxXXChukg9D3Wg3XyMGJfTZrdIYx15kVlGSQY5ewyw0gqjwQjSWqWYJSzBSMpiwQjSWqWYJSzywgj3p7zt8h4m87+lBDU6u06TO/53MjL33qg7L1xm9bfp4f47y38vfekfKsswag8sre3rPznLLLPd5Lad1Yl9a9Bl2CUs8sII8o+I7Kf0RnZ8QACwMj+bArC2LEII96jxpI/OwQjHfLlPWl0Tt635ttAvHeOPFGu7Xgsjw95KT6TGhQJRuWTvWiCLIzQ1vn8h9v4T+/YDyBsZ3+xLxew3WOJMOaNtPyfRSwDsn2C/QbCdr6EwM/2uRDD+IYd62LTlRV0glHOLiuM2MitCCN2LMq+PQfZdTZwCJ0HHYXb8e+N2fB5tcmOwe0eRoxP8YEq47HjdHKVWmYJRuUS27SVbXOc9aOt2jsA/i4CtsO8mOJv27E9UxZGfEHIvkzggcGLMZZn7xTYC0cI5duLR4Szj7EuZZRglLPLCqNu1EsQ+E6aNgPSbbrqugow6rV8O89T9mKuyhKMcvYgwkjKX4KRJDVLMMrZZYUR70v7MNxvTnrQmna1xVsJSdtxuwD5JW2j7C0ClOvvd9dFglG5lNQOeUfA/gIJlDbLSWv3TIs0/L7SZPK30tBX/K08L/Y/f9vdarK7HJNt76UEo5xdVhhBvoHymRE6EX/GhDCB+ZYdOgE7EG6jodFjOzqM7Vi8d024MS90IKxjyTzRMf1zJX4Zj/e4mY55teqIVZNgVD75gdjDiO0RbZVf/MaSLyGgzUK2zVoweIDZFxbY9hGf64QPw/gZ6+hjyDep/9kybZ+CsY3xEM519i9sZ9lM2y8JRjm7zDBiw6OSfoEBDRINkJ/R6NkZsM1uR5htsLaR27wspLgNjd12TpuXfeDKjoelr3+VJRiVT759eRhBfnDnRRXaOi+qKMQFpDyM2O/Y5jljwtK+eGBhxJkR/kstRBhBvEizZVt4Ij0uIlE/7hOhhDJRFuIiDcuCWKd+STDK2WWEERtc2qvdEAd/Xq3BFib8jO1osLbjscHys88L8ZmXvdJiZ2BHI6xsOtbdAnIQJBiVR3aGbuVhZNsj2y3CLIw4s1i2bFmUNglGhAf6H+LjLVOIgGB7R75YWhghLfKx+abBCGkQ16bnPmAd8dk3uY1xWVceg35IMMrZZYSRVD4JRlI/5Wd9ZZRglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLMFIymLBCNJapZglLN/d9HvhY2jm3yVJalJdYLR+Jf+bbi49zv+EEhSkwSjnP38rhfCb9z8W77KktSkP7v/z2NtZ1B9cOiJcPq6H/KHQJKadPzWX4m1nbK4kjCCdatOaqVTb5wKG8Y2xtrNIFu36qSWOnsijO1/JdZuyuLKwujmFxf6KktSQ3W6RUcfeeZafxgkqaEy36KDKwsjWLMjKUm4hbto9a2x9lIHa3YkJQm3cA+v+kysvZTJqTB6aOiRWOSy+ZqlfxP+5K65vupSzVXHWRF97O4rw5mbZ/lDItVcZZ8Vwa8f2hie2vV0HEa3b1wci1xG3/7y4nDfuvt99aUaCs+J6gwi+vALXwjnv7PAHx6pjjp7ohIggl8YeTGsO7C+ujCCdbtOgtAONoy9HmsfdTQGoHPLP+kPkVQzoR0c2P9yrH2U0Y8MLY2WlYYRfNUdHxSUaio8I9KMKO4De56PBqM3j+/xh0wacOEZUVVmRDSYA8VghHt3rx5cH0tQZq/dtzYalOY/+Vm/O9IACrdncb7r+rJCFh/csyoalN548Gp/+KRB1Hdvy5X9ZYUkp8IIqtrsyHr+k5+JBqq6+Nc+9p5Y2CC7Tl9ozcuHNt4TDVR18bar/m0sbJCNL7SW+XtEk3n3id0RdwYORnXz9T96VyxMluts9Ynq+Nm9qxrcSYQR9J39a2IJ5fJZHU+Wm60+UR3zFh2UCiPNjqphdTxZbrb6RDV816a7w54TexvMSYXR6fOnw8tjr8YykMtldTxZbrb6RDX86ti6JuakwgjS7Kj8VseT5WarT5Tf9vYc1RJGkIBUbqvjyXKz1SfK7SQQQZPCCELiNaPV+DZv3ayOJ8vNVp8or9NABGWCEYRM9p7cF8tcLtbqeLLcbPWJcnrx5jujdxHSlBlGEB446bZduayOJ8vNVp8ol5/Z82x4dHiZx0lMbcGIApCe2Lk8Vqjcf6vjyXKz1SfK4ZGToxErnt79jEdIojqCEfX4ziejwpbteCJsPrwlVhm591bHk+Vmq08UZ8yCwIS7Nt8TDp0+5JHRUl3BiNpxfGc0DUMl5P4aHc+HyXKdrT5RnDccfN3jIbNygZFUnNDxJEm6rG/98mPh5IEzPlgquQSjikswkqRmPfuZ9WHJnzzng6WSSzCqqA5vOy4QSVKK0Dc2Ldnlg6USSzDKQc/MXxcW/adHow7QT+tWhCSlC7frfJ/pp2/6uYfCkg9phpZVglGXQqOTJElKE6A4tuGID5acBKMuJBBJkpRFGisml2DUhdTAJEnKottmPxF2PTfmgyUjwagLCUaSJGXR81/cEFlKl2DUhQQjSZKySDCaXIJRFxKMJEnKIsFocglGXUgwkiQpiwSjySUYdSHBSJKkLBKMJpdg1IUEI0mSskgwmlyCURcSjCRJyiLBaHIJRl1IMJIkKYsEo8klGHUhwUiSpCwSjCaXYNSFBCNJkrJIMJpcglEXEowkScoiwWhyCUZdSDCSJCmLBKPJ1RWM9q46EF7+8uaGX79tOGxavKM2Box8mCzLsveSP14V2YcPjL+9I7z2je0NFgw9vDecP3XBI6Ol2obRiV0nv1vYnjC+71StDRj5MFmWZe+nr30lsg8fZB/fOR6x4pWvbfEYSVRbMELGr35ta6zQulowkmU5i+sII/rAuiMRO04fPOuR0qRMMBpdfSjKzBdSdwtGsixncZ1hRI+8eDBsvmOnx0tDmWAkECVbMJJlOYsFo0veet/u6FFPklrCSDOi1haMZFnOYsHosrc9uDu8fsuwx01rGAlErS0YybKcxYJRs19bOORxkw4jgWhyC0ayLGexYBQ3GGOVCiO9NTe5qwqjKVOmRJ72g9Man7nt53/m7dHyrkV3N4XDU98ytZEGS+Zz5W9d2RRv5aOrori+XObv82U+214ZavrMMMZnvljaONf8+TWNOvzdX/99LH8bjiU+2/pzn2zZWEeezBfHY3TrWFQ+49i8uL+Ib+tm4/PYshzk5/cX8f05sPvGcmx6G9eGJcXjvsH22HIb98mH8ZgjDPmhjv64cUlf/b4/aewL0qO8pHbDY4Z1lJUUXnULRnEPP7YvbF+yp8GcRBhtf0jfIcriqsKIAwSXtsPbsKX3LIsGEXzmwMzBwg5E3khrB02/zcLLbk+Co83PQ84PYIyDMAzOjIcwfmYeKIth3GfmjUET29JgZOvG9NhuYcN9sXWyxwx1tvHxmdBAOOpAMBAaBCriccn0+Ix4Nk+G+3hct/li/a3/4q1NMOK+st7YRwslgsXnyzLtPloY2frZcrDkueR5QpqkY141C0bJfvWGy99BSoSRbtFlc1VhhMGC9p89oPiZA6AfiGAOtjDWAbG0AYQDrQeBta8f8soCIw6CPj870DOdrT/z4ZL2sxw/M/IzOZvWwsiXg333sxIPI8axdebgzrrbfUqbRfh4Ng7rgPyYt4URZ1t+BsRzhnCmtfmyTIbTfmbEdmO381z6cLtPVbRglOwjW4+F82cu/VJDDEb4iR9Mn3wiOe6qwsgDwA4khIUdRDCwcCbBK9WkK1zmRfttfnDyZTNPn5YAQngrGNlZiB1UW82M7CDOvDmQZpkZMS5hzXALI5SJ42r3g2Y9PYw4MOOzncFgmwcv68C87azQxuNnrjNfAtPDyB5fG0Y4eOD6MllfhLWaGdkLIB53m9bmXVULRunms6MYjDQryu5BhZEdMDAoJA069grX52dnMH6Q4jqvqBluBzl+hm1eBI7PjwMY15MGL4azTMKI+fqrdIYnwYhxuI3HwpbnYYR1HKcbv3BTE/TsPlgYsUxbjh+gLWRsHez5sMeS5dEech5GTG/bA9OxTBtu11vBiOVzG+HqZ0Y23NapihaM0i0Y5eCqwkiW5f5aMEr3hm9tD6cOnInDaN2NeosuqwUjWZazWDBK956VY2H306NxGOHfQPjIcrIFI1mWs1gwSvfo2kPRK94xGOF/U/jIcrIFI1mWs1gwSvfYuiPRb9YJRl1YMJJlOYsFo3QLRjlYMJJlOYsFo3QLRjk4DxiNrD0YtjyyW5blknjrhH0/7daCUboFoxzcDYy+POPesOpz6/3hlySpBNqydE9X/dtbMEq3YJSDO22sANHK+ev8oZckqWTqtI97C0bpFoxycKcNVTMiSaqGzh4/13E/txaM0i0Y5eBOGimeEUmSVB110s+9BaN0C0Y5uJNGigekkiRVR530c2/BKN2CUQ7upJEKRpJULXXSz70Fo3QLRjm4k0YqGElStdRJP/cWjNItGOXgThqpYJSP8K8FsmrOnDlh1qxZYXx83G+KtqXlhfhI10pr1qzxQZGQbytNmzYtTJ061Qe31PTp01PraoV6c1/nz5+fuN9SdnXSz70Fo3QLRjm4k0YqGHWvJUuWNA32/P84IyMjjcF67ty50ToGYywJI6xbCCAv5gGwYBvCov/PMxF/5syZEQQYB/kgHrdjuXLlyigdP7MejIc0vs6ol62H/Txv3rzGfnDfLGBsONKwrNmzZzf2k/XOAlSptTrp596CUboFoxzcSSMVjLoXB2oM8BjEGUYjDCZoMChzkAYorDizwaDOdcKHAzkHdeZvYYVtTIcykT+g48ORhvWBCD6K0EKe3C+YQLP1RjweA+TBeFhi2+joaKNuzFvqXJ30c2/BKN2CUQ7upJEKRt2LMwwChKDgYM6BOQlGCLczFAIB2y2YoG3btjVgBCE/rPvPTId8mT/jACJY9zDCuoURZzgWRsjX3kZkvS2MEI91wJJ5WBhxKXWmTvq5992//3TYcKf+PU+SBaMcnKWRfv0dDzd9FozyF2dDVRKeGWVR1n0jgL0QZm/vSe3L9/MHr770b+TbMfI4tms8Fi4LRrn49Xt3Trj18dr26KXfuFp785bos2AkSdUSYbTj6f3R+p3vWR7r55P5ttlPxMLkSxaMcvLYa0eiBprVN/7M5Vs1kiSVX74Pt+tXFm2LjRvyZQtGfTQb5XOfe00zI0mqmNB3933nQKMfH91+PNbH5c4tGPXJX/2p+8Px3ZfvFQtGklQtAUC2T3/+X90d6+dy5xaMCrJgJEnVkoeRnK8Fo4IsGElStSQY9daCUUHuJYz4pcxOlfZ9FH5vJenV4V4J36VJE7/Xk7dalZn03SQrHBv7pdg0+S/dtiNbP1+Wf7XbtwV+ebZV+0Be3dQvSe2+Vo5X3u3xQ5vsZ7tLkmDUWwtGBbmXMGLHbzWodqJOYZQGN6rVwNdqH9Jg1O7AZ4U8W5UJGLG+Sd8R6sf3eWz97Bd6IfuzRRacrHPaMWtX7eSD49TuMfEwavUbf0nnoRcSjHprwagg9wNG6KQYhGB+i99ux8DJbezQ/KUA3/n5m2uEEdJg4IMYxjT8pQEI+XJwTIOZ/4kbiIMdPjO9HwBZBvLkLxuwDKRbsGBB037YY4C62zraOHaw576yjkiP335DeNIg6GFk9xVpOevgzwVhO+vtIWjPD5e+fpzl8Nhgac8/49iZkxXrgDSsl60jy2Rcyh5Le34h7jM+I46FET4nnQMr5OdhZPcZbdF+tm2slxKMemvBqCD3A0bssPjBTcjCiMCYDEYcjDigECbI2w46WWFkxfrZgd4OeFhHHDuA+gERIowoDoJYAhxWNn1WGFmxjhhI84aRlT8/aTDiPvhyLSygPGBkNRmMuA3LNBhB9ryx3DQYsR7Y5mEEYXsS3PKSYNRbC0YFuZcw8rKdPy/5QVrKpiTwlEm8MOhGg9o2BKPeWjAqyFv7BKOkq9o81AvADbpwxW+v6Msm3M5LeimjHSGPQW0bglFvLRgV6C1L9/jDLklSSSUY9daCUYFG45Ykqfxa/FtPhmfnr4v1YTk/C0YFG0A6e/ycP/ySJJVEANG627fH+q6crwWjEpg/vChX35/70Tsj+3C5utaMqD8WjGQ5R+MtycW/1f7/uZHlulswkuUcLRjJcmcWjGQ5RwtGstyZBSNZztGCkSx3ZsFIlnO0YCTLnVkwkuUcLRjJcmcWjGQ5R1sYrV24NbZdluVkC0aynJNv/oVHLn035ccufT/Fb5dlOd2CkSzn5OO7Tza+KPnyNzUrkuV2LBjJco4mjHy4LMutLRjJco5ec+Pm6HadD5dlubUFoxL46PCJ8OWZ90VX1LfNfiLc9XtPy7JcoDnD3XT/zlh/lXtjwagERqPf8+IBfwokSSpYeBll4S8+Euuzcv4WjAr0q7dui0AkSVK5hX8j4fuvnK8FowItEElSNYS+enjL8VgflvOzYFSgX71tuz/skiSVVHpLsrcWjAry8PJ9/pBLklRiCUa9tWBUkPGzMZIkVUeCUW8tGBVkwUiSqiXBqLcWjAqyYHRZU6dObazPmTMnWo6MjIQpUy41Sy4hxrVpeiGU361mzZrVVM9264z04+PjTXXh5+nTp0des2ZNmD9/fmNp40Esk8cQcZAv8sD6kiVLGmlsPCvmVXcJRr21YFSQBaPLSoMRBk0MlgsWLGhsR1wMmBhImY4DKsIxcHJAxWBt00AYtPGZAzLKY5m2HoiPz3bwRzymxxLbCAWIdYYIiCQYMT33A/kwXRIMEJeyebAMpOG+QxZeiEOwY3srGHFfEAYThjw+dZdg1FsLRgVZMLqsVjDCILp169bGdg7kGDRtOnzm4Akh3WQw4kCbBCMO6IhD6CTBCPlYGFFpMLL18DAiJOysECIwPLRYH86IWA8LGMbn/trZE2HEY0moCUbJEox6a8GoIAtG5REHbw7maeIgPVk8alAGcQK+7hKMemvBqCALRpJULQlGvbVgVJAFI0mqlgSj3lowKsiCkSRVS4JRby0YFeRewOjIkSOyLBvnKcGotxaMCnIvYCRJUu8kGPXWglFBFowkqVoSjHprwaggC0aSVC0JRr21YFSQqwYjfvkRX8j0PyFD8Xs19hcDkjRt2jQflKoZM2ZES/vlTSvm1eq7P/ziqv3CJ+povzDaiVgmf+UAmj17drTkrztwSfHY+P0YlO8kDbIEo95aMCrIZYXRwoULwxVXXOGDI/EnaCAMnhzk+WsJHFD5ywAQwvlNfmjmzJkNgLSKQ61du7YJgH4QtzDi4G9/EYG/MkAYsRwLI8IES/5iAutiy0OY//kciOm531hPA67dZ5bBX4HgrzGwnsxLKocEo95aMCrIZYURQJT0+2hW/OkdDvIQB1SIgyh/1gbmOtJhoOagmxaH4iCfBAfIDvosn/nZGQvLI0wsjAgV5M08EB952J/zSYORLxf52JmaXbeA8ccO8ZAeS5bPOFLxEox6a8GoIJcVRq2EQZagwiCJz3ZA5e+Z2QGXgyyEtPgMgHDgRvqkOBRnLBTTEQpJMEL5rCfy5eCOfBCH5RJYEON7GLW6/cdtiGvj2dmjBwpnRhY4hBGEz9hnuw9pt0Wl/kow6q0Fo4JcRRhZccCUpLpIMOqtBaOCXHUYSVLdJBj11oJRQa4ijPhMxz9Ut7fVrHhrrB3xNlxannmL5fnnQZCvu/+cRf5Ypcnu82T16Fb9OraDJsGotxaMCnLVYIRB1Q6SfN7BFwwgDup8ZkQY8X/lYJ1p+DwEy6T/Z8QltsH8jGdEzAfiQ3/I3jpEuK2vrwPF5zl41sUXMrgdcS0I5s6d29iG+rDeFiR2O/eV8ttYV5Rh49l6Y93Dg2ntsybsL+pj6894fLbH+iANn//xXHC7br2mSzDqrQWjglxWGKW9Tce3z7z4UoAdMD2MIA6wiMdXt5nWCmXDTIc8YOaHfLgNYRiEWTfCiOs+b1sHiuVxO/LmfuI7ThYSTMcwDOgQ4/Mzlmlx7TaGUbYeFI6VnbXZbYQlgcrPrA/K8eeNx5xlc93up5Qswai3FowKcllh1EqcCWDJwYyDGwdJhCOMswyucwC2gx8HzqQBn2+nIS0HU5bPbR5GhAnLtW+4+TpQHMi5DzYOB3eKb8BB2Ac7o7Nx7Tbum62XhxE+83hgyWNpjw3j8jNmiAjzb/HZ+lsY+fNly8Y6j7H9jpfULMGotxaMCnIVYSRJdZZg1FsLRgVZMJKkakkw6q1TYbRZMOqpqwYj3B7i8xX73KJbtfpSKWRfXvCyz0PS4lC8LVVG2VtzVpMdm6Q0RcrXF/vFFyNYV7YjLHHueGuznduDvhwv3hLNW4JRb30gDUYbbx2ORZbzcxVh1OnglzY4ACCtBpakNFbtwKjMSjq2neyPfVEhq9J+Q68T+XPJZ3qQfWbGz6gvyxeM5NHVh8LQw3vjMHr5y5tjkeX8XFYYpb1N5wdMDCR80w2yD87tLAQDBwcHP8BaGCE/+5YdZPOG7SDDwczDCIObzZPbUSefH4QyWR63URw8+TIG8rDHwNaTefqXFCCk4zHBktuwjrraY8sljw0/Y50Dt40LIz222WPBcIovSEB2MOeLEBDrhX3wAz7y5kzH7h+On62jFctHfM6OGMaZEWdHFkYIs23Iz45RDsuyx4J1E4yq6aGH94SD648KRv32nhcO+ENeCqX9ane7MGI41u3gYK/eOeAy3F8de3gwH9YlC4y4zdaJ+XlxAGQ6DyOoWxhB3IYwCyO/P3nBiPtuoQshTrcwgjyMWC7iMm8LCwhL7i/ySoIR9wd1RJ4LFiyIPnsYcd+Zv2BUTa+7aWt448S5OIzW3bg1HNl2PJZAzs9Pfeplf9glqfayMzorf7HST42PnhaMemxMgKAYjA5uOBa23rs7lkDOz2jckiQ1KwlGmCklhfdLC/7vB8Om+3fG+rCcnzcsGoqOdQxGkG7V9daYeQpIklRuDa8YCc9d/1qs/8r5ef93DjWOdyKMEMEnkvP19mV7w8L/uNQfekmSSiDcStftud6bt+igRBhBmh31xyvnr4savVxtf/NffzayD5erad9P5fz9+m3DYf/qSWZG0Lb79dxIlrP64LJVYdvv/2EsXJblZNtZEZQKIwiRT+w9GctEluVmC0aynN0eRFBLGEGvfm1LLCNZlpstGMlyNieBCJoURhASHx06EctUluVLFoxkeXKngQjKBCNo76oDYfOd+hFVWU6yYCTL6d7z9GhLEEGZYQTt/m6GJ/boOZIsWwtGspzsLffsChtvH/Y4iaktGFHj+05HUIJ3PbU/Vrgs182CkSxf8tGtx8P6hdsjPoy9ctjjI1UdwYg6f+bCxPRrrAEmWa6rX/nr+8L6d783Fi7LdfP6m7eFU6NnPC4mVVcwkiTpkk6uXh2G3/9+HyxJUkYJRpKUgwQjSepOgpEk5SDBSJK6k2AkSTlIMJKk7iQYSVIOEowkqTsJRpKUgwQjSepOgpEk5SDBSJK6k2AkSTlIMJKk7iQYSVIOEowkqTsJRpKUgwQjSepOgpEk5SDBSJK6k2AkSTlIMJKk7iQYSVIOEowkqTsJRpKUgwQjSepOgpEk5SDBSJK6U1swOnrzzeHoTTeFYwsXhhP33BPG77tfluUJH7z+82Hb7NmxcFmus4/femvEDPjM2rUeKU3KBKPjixdHmV3cvS+Eg0dkWXY++eRTYXjOH8TCZVm+5FPLHos4kqaWMALJosQJGcuyfNmCkSxnc3Rn7d57PW7SYQQQnVu/IZaRLMtxC0ay3J5xx80qFUaaEclydgtGstyeT3x7cTjz0ksN5iTCKCJWQmJZlpMtGMly+z5xxx0N7iTCSLMiWW7PgpEsd+Y3Nm2KuBODEV7f1ltzstyeBSNZ7sx8wy4OI82K5Jw9ZcqUhvmZ26a/9a3Rcs3EYG7DuW3qW94Src95z+828mAan78vd2TDptSykYfNE2ZZPr9ZP/tz0XL+J/4mWl9y27eb0iGMMPJpuY79Y/52mw9jeTYPxmEevnzm5cvlcUJ+3Afss123+SA+ysA2rPv8bB1sfWW5Gx/9+tfDm2+8EYcRXrvzkWW5G3PwwmA+vnNP0yDHARNx1i5fEQ20jMuBH2kwcPp8YQyO2O7LggEj5kcjX5TPARnrNr0FHeJi6WHE7dwPwmjhj/xI0zbuK+rkB3HWzeZn09r99TBiepZv82VZLJf52f1N22fCyG5nGWn7Icvd+uzzL4bTzz8fhxF+WcFHluVuzAHQDmw0B0JuszCwaexVPCEBEy6MZ21nRnYAtXFtXViGzycLjA4+vLQJRhzYUW7aII70HpbMz4J0MhjZOmMfeEywjjScGSE/1Avr9hgmwYjbUB7KarUfstyNz7++KZxcujQOI/yEg48sy93YD152sMMAyBkEjcGPAya2YRBNmxlxILWDK500M+JgbGcNSbMEmGUSQPhs62FhlDYzsuUkARHl2TwtXBmH6QgTrGeZGfG48njafJmWdeAybWaUth+y3K3Pb9wcxh96SDCSe28/ePmBkNDBZz7T4KDIgdHOjGx+Np4vyz8zsrcIEc8P/DYO7G9twcjT7wdhtO6//mYjHgHD+mBp6+bhwHw9sOz+wYSrhZGts59p2jpy3ZfjYWSfSRHyafshy91aMJLlHK236WS5MwtGspyjBSNZ7syCkSzn5KH3vrcBo/2f/odwdPGdsTiyLCdbMJLlnHz09sXhtZkzI2/9lV+JbZdlOd2CkSznaMIojB2KbZNlOd2CkSzn6M2/9EuXYJSwTZbldAtGJfPFvfuj5w5yNT3+xPIwOv8fY+FydXxq1Quxfin33oJRCXz8/gejq+kDN9wQwptv+lMhSVKfdWzp0qhP7vvEJ2P9Ve6NBaMSOLqtI0lS6TT8vveF137yJ2N9Vs7fglGB5oxIkqRya8cf/VGs/8r5WjAq0AKRJFVDeiml9xaMCnT0jEiSpNLrzfPnBaQeWzAqyHhrTi8rSFJ1JBj11oJRQcYrpJIkVUeCUW8tGBVkwUiSqiXBqLcWjAqyYFSsRkZGmtaj//Ezofnz50dLfp4+fXqYOnVqY9uaNWsa26Dx8fEwc2KQwpLpRkdHo+XKlSsb6ZAPNG/evKb0zBtasmRJU13wec6cOdE60iN81qxZjfhSfyUY9daCUUEWjIqTBRHU+AdyE9CACQiABxAAAAAbbAMgEJfw4TYsCRwIEEF6lIV1pKMJPMjDCJ+ZH9bhuXPnNiBoQSb1V4JRby0YFWTBqFhxxgEAYODnrAdLbCOwPIzwmVCBCBMssZ3wIYy4jXlMBiObP9IgHwII+SFMKkaCUW8tGBVkwUiSqiXBqLcWjAqyYCRJ1ZJg1FsLRgVZMJKkakkw6q0Fo4IsGElStSQY9daCUUEWjCSpWhKMemvBqCALRpJULQlGvbVgVJAFI0mqlgSj3lowKsiCkSRVS4JRby0YFeSywghfquQXK+0XMq3slzazyv6sTZL4UzidCOn4JdTJxC+vdqukL58mhbVTN4rHqpXs8eSXa3sl/NwRxF+GSCsvaf8HSYJRby0YFeQiYXTFFVeEhQsX+uBosLG/jcZfDkAYfyoH4hIDIdf5czr8uRwbD7KD57Rp0xqDNAY2+zM5/DkcCPHsQAghjv01BIh58dcLsJ2/XGDLwBLbuF+UBTDEMpAvfxKIAzB/ZQHxmSeFMFs/yMMI21hPbMM6jyN/oYE/H2T3C8eB+wZ5GCXV1Z4/5knx2Ni6ct3+egSEsvnrFDxOTG/FbTye9lwwLtLhM36/D+L5rYIEo95aMCrIZYQRBhD7+2f8bTRqMhhx4Ev6/TR7tW9hBBEWCMO2pCtvxkUZdtCE7KBtB2kOzNZMy/IIACsOqhYYrJMdcCFspzgI++3M3wLV15NCOg7eLJ/icYLs8bTHz9YV66wH4ts0tkyu89gQbhSAASM98uM5ZxoK2+zxZHkWRha8/FwVCUa9tWBUkIuEUa+VBCMpWYSFVH4JRr21YFSQBxFGnBX5mYYUF4+VnVlI5ZZg1FsLRgV5EGEkSYMswai3FowKchlhxGcofLaSl5CffV7hhf/Xg2cHnZRpH8BbtXoWkVYOn5O0e+uMz6M6Vdo+dCI+1/FqdfxbqdVxrJsEo95aMCrIRcIo7QUG/yo3PmOAxuDG50B8gI1wbMdgxQfnTI84fAiOMMKIb8oh3D5sxzbCCOuEon1Dz+dP4cG6faECQp5YRzrmSTE/hCMfG8fCCPbpCA1bPupoYcRblKwTH97zs315gceG+SLcvihhAc1jyn3jMWLeNg/E9W8hskzEseeZx2nbtm2NeNw/niN7jNgOEMZjxvPDfeebf4Mmwai3FowKcpEwwoACIHn5q2AOWvYNOw7mhBSMgcrDwr7RReDYwZ0A8jCygzqfP3EA9S9GEFiElocRB1Ws27f9mBZpEBfbPIxYPsU8uJ/cV+4DbAdg5LVixYowe/bsyMzPwohvFdq6ENQWMhD3E2ltOOLBqI+FEfKw9WeZPG8U1y20eFx5Xu1x5DFGPigPZt24/77sQZFg1FsLRgW5SBi1EgcWiAM1w6FWMOLAhLA0GNn8OMhxkEc+Fjoc4JAv4vqZEZdcZ/4sD+KgSnFA9TBCesII5SC9nUFAiIc4CLf7TRjZ+kCc+RBUSG+hnAYjCHnh9iXrbgf4JBgxX8LIwxSfEY76Wmj6c2z/xTnkj6OHEUQQMl+WjThsB4Mgwai3FowKcllhJHWuPL/AicGdA79UDglGvbVgVJAFI0mqlgSj3lowKshlhJG9XWOXft2Lt5Bg3rpJkr/tlSTmkyVuu7IzDZbjw5Pkb21lkc2/lfytPcgeT2znrUse26x5t1K7+5OHeDvSyh977G/SMcmiTtNllWDUWwtGBbmMMEJnxmAxb968xjMhDoR2YOQDbso+FMd2DqZ8/oF1PmSH+EyBedi8+IwCsnnaZy2sC565QPb5iAWHzZfPY+zzIwhx7YCIdVsvpGOe9lkK47JuafvAZzisP48Blnz2BPnjaWHB/eTSP4fhcyt7jCDmjTA8C7L7ZY8ln8lxH/2FAOLguCEO4q5cuTIq09adx5XHzC4hrNs3HxkX+djnYciTx4vpWD8IeVx//fWNdQrpbX18HZCfP3/tSjDqrQWjglwkjNAhk96mswMRfyOOn5GGgzkBZR9mcyDgIIUBBAOAHeiZDsIyaWCwgylkBxiYryBDFkZI1wpyDPdX4pANI0C579wH5E0Ic+BFHJjgYHgSjCDkxzozLrYRgPZ4JsHIvrjAzxDqwDQ2DstFHRiXxw9puD8EAsTjxPjIA58RH0Iau//cjn2zoEGZNi/uG+P4/GEeKxjb2d64nfsJYck6MQzp7HnjCyJM789fuxKMemvBqCAXCaM0oZNy0ECnhSyMOBCx03PQtTDiwIR4dhDkTADhSItwDiYsC7IDOQccDnrYhvQItwMcYYRtDGe5duCEPOwgCyMOgojHfSSMbHmQrRsHRIrHiscLwpLHk7MQDrw2XhqMWD73xS+R3u4L6s59Qbg9FghjHSyMsI4wls8ltmMb6sJzgPKwnduYB+KwTOaBuDzvzA/Cued+YxvWYZTBY8XziTQ2nRXrY8+bBb+vTycSjHprwagglxFG0uDKzlq6FaFWpJIuKnotwai3FowKsmAkSdWSYNRbC0YF+dzGLf6QS5JUYglGvbVgVKCPLV3qD7skSSWVYNRbC0YFOmrckiSVXht+6qfCqVUvxPqwnJ8FowK97xOfDMPve58/9JIklUyaFfXeqTA6fuutschy/j5+/4Nhz8c/7g+/JEklEG6lC0T98Rur14ZTzzwTh9HRm26KRZZ74x1/9EdRg3/z/Hl/GiRJKkgjn/mMQNRHn3zo4XBu+3bBqAzGG3b7/+f8MDznD2RZLsg7r7o6nFzxTKx/yr11xJwJxWB0Zu3ElGnZY7EEsizLspy3j333v0/HYARpdiTLsiz32qeeXN7gTiKMoIhWCYllWZZluVufWfF0OH733Q3mpMLoxL33xhLLsizLch7msyIqFUbQ8cWLw4lvL45lIsuy/P+3cy8nAMJQEEX7r8EGrMASghYgKUMQUYPgkwkEgn9d34GzzXbI5wX4QzuifREpt2WkTE1jfVkeFgQA4AvdEeVHc3keyygleB/brCsKm11tS+vj5CwAAGc00Ko5InVHejV3lddllLKGYKNzNlRV/MIBAIAz+llBA61vsgExw1NDjrBrfQAAAABJRU5ErkJggg==>
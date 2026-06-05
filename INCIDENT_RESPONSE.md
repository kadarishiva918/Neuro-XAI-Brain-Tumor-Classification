# Incident Response & Runbook

**Brain Tumor Classification System**  
**Incident Response Procedures**  
**Version 1.0**

---

## Table of Contents

1. [Incident Classification](#incident-classification)
2. [Severity Levels](#severity-levels)
3. [Response Procedures](#response-procedures)
4. [Escalation Procedures](#escalation-procedures)
5. [Communication Plan](#communication-plan)
6. [Post-Incident](#post-incident)

---

## Incident Classification

### Type 1: Performance Degradation

**Definition**: Model accuracy drops > 2% or inference latency increases > 50%

**Detection**:
- Automated alerts from monitoring system
- Alert: Model accuracy < 93%
- Alert: P95 latency > 1.5s

**Investigation**:
```bash
# Check model status
python model_registry.py current

# Check recent predictions
SELECT * FROM predictions WHERE created_at > NOW() - INTERVAL '1 hour' 
ORDER BY created_at DESC LIMIT 100;

# Analyze accuracy
python evaluate.py --model current --output metrics.json

# Check input data quality
python analyze_data_quality.py --recent 1000
```

**Response**:
1. ✅ Acknowledge alert
2. ✅ Check if data quality changed
3. ✅ Compare with baseline model
4. ✅ If accuracy < 90%, initiate rollback
5. ✅ Prepare retrained model
6. ✅ Canary deploy retrained model
7. ✅ Monitor for 1 hour

**Timeline**: Detection 1-5 min, Investigation 5-10 min, Resolution 10-30 min

---

### Type 2: Service Availability

**Definition**: API returns > 5% errors or latency > 3s

**Detection**:
- Automated monitoring
- Health check failures
- Customer reports

**Investigation**:
```bash
# Check pod status
kubectl get pods -n production

# Check logs
kubectl logs -n production deployment/brain-tumor-api --tail=100

# Check resource usage
kubectl top pods -n production

# Check dependencies
python advanced_monitoring.py health --api http://api:5000 --db $DB_URL
```

**Response**:
1. ✅ Scale up replicas
2. ✅ Check database connectivity
3. ✅ Check Redis/cache status
4. ✅ Review error logs
5. ✅ If unhealthy, initiate failover
6. ✅ Deploy fix or rollback
7. ✅ Monitor recovery

**Timeline**: Detection 1 min, Response 2-5 min, Recovery 5-15 min

---

### Type 3: Data Issues

**Definition**: Input data corruption, database inconsistency, or data pipeline failure

**Detection**:
- Data quality checks fail
- Database constraints violated
- Pipeline errors

**Investigation**:
```bash
# Check data pipeline status
python check_data_pipeline.py

# Verify database integrity
psql -d brain_tumor_db -c "SELECT COUNT(*) FROM predictions WHERE accuracy IS NULL;"

# Check recent uploads
aws s3 ls s3://brain-tumor-data/uploads --recursive --human-readable
```

**Response**:
1. ✅ Stop accepting new predictions (if data corrupted)
2. ✅ Investigate root cause
3. ✅ Restore from backup if needed
4. ✅ Fix data quality issues
5. ✅ Resume operations
6. ✅ Validate data

**Timeline**: Detection 5-30 min, Investigation 10-20 min, Resolution 30-60 min

---

### Type 4: Infrastructure Failure

**Definition**: Kubernetes cluster issues, storage failures, or network problems

**Detection**:
- Node failures
- PVC mounting issues
- Network connectivity problems

**Investigation**:
```bash
# Check node status
kubectl get nodes

# Check PVC status
kubectl get pvc -n production

# Check network policies
kubectl describe networkpolicy -n production

# Check cluster events
kubectl get events -n production --sort-by='.lastTimestamp'
```

**Response**:
1. ✅ Check node health
2. ✅ Cordon unhealthy nodes
3. ✅ Drain workloads gracefully
4. ✅ Repair or replace node
5. ✅ Uncordon when healthy
6. ✅ Verify service recovery

**Timeline**: Detection 2-5 min, Response 5-10 min, Recovery 10-30 min

---

### Type 5: Security Incident

**Definition**: Unauthorized access, data breach, or security vulnerability

**Detection**:
- Intrusion detection alerts
- Unusual API patterns
- Security scanner findings

**Response**:
1. ✅ **Immediate**: Isolate affected system
2. ✅ Revoke compromised credentials
3. ✅ Review access logs
4. ✅ Patch vulnerability
5. ✅ Deploy fix
6. ✅ Enable additional monitoring
7. ✅ Notify affected users if data exposed

**Timeline**: Detection 5 min, Response 10 min, Recovery 30-120 min

---

## Severity Levels

### Severity 1 (Critical)

**Criteria**:
- Complete service outage
- Data loss or corruption
- Security breach
- Major accuracy degradation (>5%)

**Response**:
- Immediate escalation to VP Engineering
- All hands on deck
- Update status page every 15 minutes
- Post-mortem within 24 hours

**SLA**: 
- Response: 5 minutes
- Resolution: 1 hour
- Root cause analysis: 24 hours

### Severity 2 (High)

**Criteria**:
- Partial service degradation
- Multiple errors or failures
- Moderate accuracy drop (2-5%)
- Performance issues

**Response**:
- Escalation to Engineering Manager
- Dedicated team assigned
- Update status page every 30 minutes
- Post-mortem within 48 hours

**SLA**:
- Response: 15 minutes
- Resolution: 4 hours
- Root cause analysis: 48 hours

### Severity 3 (Medium)

**Criteria**:
- Minor performance issues
- Single component degradation
- Low error rate (<1%)
- Can be addressed during business hours

**Response**:
- Escalation to on-call engineer
- Monitor and document
- Status page update once
- Quick post-mortem

**SLA**:
- Response: 30 minutes
- Resolution: 24 hours
- Root cause analysis: 1 week

### Severity 4 (Low)

**Criteria**:
- Cosmetic issues
- Non-critical features affected
- No customer impact

**Response**:
- Log for later investigation
- Include in sprint planning
- No SLA required

---

## Response Procedures

### Immediate Response (0-5 minutes)

**Step 1: Acknowledge & Assess**
```bash
# Acknowledge in incident system
echo "Incident acknowledged at $(date)" >> incident_log.txt

# Page on-call engineer
python notify_on_call.py --severity $SEVERITY

# Get basic system status
kubectl get all -n production
```

**Step 2: Prevent Escalation**
```bash
# If error rate high, scale down traffic
python deployment_manager.py scale --replicas 1 --environment staging

# Or failover if needed
python disaster_recovery.py failover --from us-east-1 --to us-west-1
```

### Investigation (5-15 minutes)

**Step 3: Gather Information**
```bash
# Collect logs
kubectl logs deployment/brain-tumor-api -n production --tail=1000 > logs.txt

# Collect metrics
python advanced_monitoring.py export --output metrics.json

# Check recent changes
git log --oneline -20

# Review monitoring dashboard
# Visit: https://grafana.example.com/d/brain-tumor-api
```

**Step 4: Identify Root Cause**

Use investigation checklists:
- Model issues: Check model version, accuracy, recent retraining
- Database issues: Check connectivity, locks, disk space
- API issues: Check logs, recent deployments, dependencies
- Infrastructure: Check nodes, storage, network

### Resolution (15-60 minutes)

**Step 5: Execute Fix**

Options:
1. **Quick Fix**: Patch and deploy (5-15 min)
2. **Rollback**: Revert recent change (5-10 min)
3. **Scale Up**: Increase resources (2-5 min)
4. **Restart**: Restart failing components (1-3 min)
5. **Failover**: Switch to standby (5-10 min)

**Example - Rollback to previous model**:
```bash
python model_registry.py list
python deployment_manager.py rollback --environment production --version v0.9
python deployment_manager.py health --environment production
```

### Verification (60+ minutes)

**Step 6: Verify Fix**
```bash
# Check error rates
curl http://api:5000/metrics | grep error_rate

# Run smoke tests
pytest tests/test_api.py -k "smoke"

# Verify accuracy
python evaluate.py --model current

# Monitor for 1 hour
watch -n 5 'curl http://api:5000/health'
```

---

## Escalation Procedures

### Escalation Path

```
Level 1 (On-Call Engineer)
    ↓ (No progress after 15 min)
Level 2 (Engineering Lead)
    ↓ (No progress after 30 min)
Level 3 (Engineering Manager)
    ↓ (No progress after 60 min)
Level 4 (VP Engineering)
    ↓ (Critical - immediate)
Level 4 (VP Engineering)
```

### Escalation Checklist

- ✅ Notify next level (call or Slack)
- ✅ Brief on situation and attempts
- ✅ Document in incident tracking system
- ✅ Update status page
- ✅ Assign additional resources

---

## Communication Plan

### Internal Communication

**Immediate** (Alert sent):
- Slack: #incidents channel
- PagerDuty: Pages sent to on-call
- Incident tracking: Create ticket

**Every 15-30 minutes**:
- Brief team on status
- Update ticket with progress
- Post to #incidents channel

**Resolution** (when fixed):
- Announce resolution
- Schedule post-mortem
- Close incident ticket

### External Communication

**Status Page Updates**:
- Acknowledged: "We're investigating..."
- In Progress: "We've identified the issue..."
- Resolved: "Issue resolved. RCA coming tomorrow..."

**Customer Notifications** (if applicable):
- Major incidents: Direct customer contact
- Post-incident: Email summary and RCA

---

## Post-Incident

### Immediate (Within 24 hours)

1. **Write Incident Report**
   - What happened
   - When it started/ended
   - Root cause
   - Duration and impact
   - How it was resolved

2. **Schedule Post-Mortem**
   - For Severity 1-2: Within 24 hours
   - For Severity 3-4: Within 1 week
   - Attendees: Team + stakeholders

3. **Notify Stakeholders**
   - Email summary to team
   - Include link to post-mortem

### Post-Mortem (24-72 hours)

**Meeting Format** (1 hour):
- 10 min: Timeline review
- 10 min: Root cause deep dive
- 15 min: What went well
- 15 min: What could be better
- 10 min: Action items

**Key Outputs**:
- Root cause analysis
- Contributing factors
- Preventive measures
- Action items with owners and dates

**Action Items Categories**:
1. **Preventive**: Stop this from happening
2. **Detective**: Detect faster if it happens
3. **Responsive**: Respond faster when it happens

### Prevention & Improvements

**Update Runbooks**:
- Document new procedure if needed
- Test runbooks
- Share with team

**Implement Safeguards**:
- Add monitoring/alerting
- Improve tests
- Add circuit breakers
- Improve documentation

**Capacity Planning**:
- Review if infrastructure needs upgrade
- Check if model needs optimization
- Plan for growth

### Metrics

**Track for Each Incident**:
- Time to Detection (TTD)
- Time to Response (TTR)
- Time to Resolution (MTTR)
- Mean Time Between Failures (MTBF)
- Customer impact (minutes × users affected)

**Goal**: Reduce MTTR by 30% each quarter

---

## Contact Information

### On-Call Rotation

```
Monday-Friday, 9 AM - 6 PM PST:
  - Primary: ops-primary@example.com
  - Secondary: ops-secondary@example.com

Friday 6 PM - Monday 9 AM:
  - On-Call: Check PagerDuty schedule

Phone Numbers (for critical incidents):
  - On-Call: +1-555-ONCALL
  - Manager: +1-555-MANAGER
  - VP: +1-555-VPENG
```

### Escalation Channels

- Slack: @on-call-pagerduty
- Email: incidents@example.com
- Phone: +1-555-ONCALL
- War Room: https://zoom.us/j/WARROOM

---

## Tools & Commands Reference

### Monitoring & Alerts

```bash
# Check system health
python advanced_monitoring.py health --api http://api:5000

# View recent alerts
python advanced_monitoring.py alerts

# Check for incidents
python advanced_monitoring.py incidents
```

### Deployment & Rollback

```bash
# View current deployment
python deployment_manager.py status --environment production

# Rollback to previous version
python deployment_manager.py rollback --environment production --version v0.9

# Canary deploy fix
python deployment_manager.py canary --model models/fixed_model.pth --percentage 10
```

### Disaster Recovery

```bash
# List backups
python disaster_recovery.py list

# Create backup
python disaster_recovery.py backup --type model --source models/best_model.pth

# Restore from backup
python disaster_recovery.py restore --backup model_backup_v0.9.pth --target models/best_model.pth
```

### Multi-Region

```bash
# Check regional metrics
python multi_region_deployment.py metrics

# Failover to region
python multi_region_deployment.py failover --region us-west-1
```

---

## Quick Reference: By Issue Type

| Issue | Quick Fix | Command |
|-------|-----------|---------|
| High Error Rate | Scale up | `kubectl scale deployment brain-tumor-api --replicas=10` |
| High Latency | Check GPU | `kubectl top pods \| grep brain-tumor` |
| Model Accuracy Drop | Rollback model | `python deployment_manager.py rollback` |
| Database Down | Restore backup | `python disaster_recovery.py restore` |
| Pod Crashing | Check logs | `kubectl logs deployment/brain-tumor-api` |
| Network Issues | Check policy | `kubectl describe networkpolicy` |
| Disk Full | Check PVC | `kubectl get pvc` |

---

**Remember**: Stay calm, follow the runbook, communicate clearly, and help the team succeed!


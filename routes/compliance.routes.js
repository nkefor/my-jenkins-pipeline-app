const express = require('express');
const router = express.Router();
const ComplianceRequirement = require('../models/ComplianceRequirement');

// Middleware to protect routes (will be implemented later with Firebase Auth)
const protect = (req, res, next) => {
  // For now, just a placeholder. In a real app, this would verify a JWT token
  // and attach user info to req.user
  req.user = { _id: '60d5ec49f8c7a4001c8e4d5a' }; // Mock user ID for testing
  next();
};

// GET all compliance requirements
router.get('/', protect, async (req, res) => {
  try {
    const requirements = await ComplianceRequirement.find();
    res.json(requirements);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET a single compliance requirement by ID
router.get('/:id', protect, async (req, res) => {
  try {
    const requirement = await ComplianceRequirement.findById(req.params.id);
    if (!requirement) return res.status(404).json({ message: 'Compliance requirement not found' });
    res.json(requirement);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// POST a new compliance requirement
router.post('/', protect, async (req, res) => {
  const requirement = new ComplianceRequirement({
    title: req.body.title,
    description: req.body.description,
    regulation: req.body.regulation,
    category: req.body.category,
    status: req.body.status,
    dueDate: req.body.dueDate,
    assignedTo: req.body.assignedTo,
    notes: req.body.notes,
    reminderEnabled: req.body.reminderEnabled,
    reminderDate: req.body.reminderDate,
    reminderFrequency: req.body.reminderFrequency,
    createdBy: req.user._id, // Assign the user who created it
  });

  try {
    const newRequirement = await requirement.save();
    res.status(201).json(newRequirement);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// PUT/PATCH update a compliance requirement by ID
router.patch('/:id', protect, async (req, res) => {
  try {
    const requirement = await ComplianceRequirement.findById(req.params.id);
    if (!requirement) return res.status(404).json({ message: 'Compliance requirement not found' });

    // Update fields if they exist in the request body
    Object.assign(requirement, req.body);
    requirement.lastUpdated = Date.now();

    const updatedRequirement = await requirement.save();
    res.json(updatedRequirement);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// DELETE a compliance requirement by ID
router.delete('/:id', protect, async (req, res) => {
  try {
    const requirement = await ComplianceRequirement.findByIdAndDelete(req.params.id);
    if (!requirement) return res.status(404).json({ message: 'Compliance requirement not found' });
    res.json({ message: 'Compliance requirement deleted' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;

const mongoose = require('mongoose');

const ComplianceRequirementSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true,
  },
  description: {
    type: String,
    trim: true,
  },
  regulation: {
    type: String,
    required: true,
    enum: ['GDPR', 'HIPAA', 'PCI DSS', 'Other'], // Example regulations
  },
  category: {
    type: String,
    trim: true,
  },
  status: {
    type: String,
    enum: ['Pending', 'In Progress', 'Completed', 'Not Applicable'],
    default: 'Pending',
  },
  dueDate: {
    type: Date,
  },
  assignedTo: {
    type: String,
    trim: true,
  },
  notes: {
    type: String,
    trim: true,
  },
  lastUpdated: {
    type: Date,
    default: Date.now,
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User', // Assuming a User model will be created later for authentication
  },
  // For reminders
  reminderEnabled: {
    type: Boolean,
    default: false,
  },
  reminderDate: {
    type: Date,
  },
  reminderFrequency: {
    type: String,
    enum: ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Annually', null],
    default: null,
  },
}, { timestamps: true }); // Adds createdAt and updatedAt timestamps

module.exports = mongoose.model('ComplianceRequirement', ComplianceRequirementSchema);

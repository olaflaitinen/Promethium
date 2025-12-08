# Frequently Asked Questions

This document answers common questions about Promethium.

## General

### What is Promethium?

Promethium is an open-source framework for seismic data recovery and reconstruction using AI/ML techniques. It supports standard seismic formats and provides both a web interface and API.

### Who is Promethium for?

- Exploration geophysicists
- Seismologists
- Research institutions
- Oil and gas companies
- Engineering firms

### What license is Promethium under?

Promethium is licensed under CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0). Commercial use requires a separate license.

---

## Data Formats

### Which formats are supported?

| Format | Read | Write |
|--------|------|-------|
| SEG-Y | Yes | Yes |
| SEG-2 | Yes | No |
| miniSEED | Yes | Yes |
| SAC | Yes | Yes |

### Can I add custom format support?

Yes, Promethium has a plugin architecture for custom readers and writers. See [Developer Guide](developer-guide.md).

### What is the maximum file size?

There is no hard limit. Streaming I/O handles files larger than available memory.

---

## Models

### Which reconstruction models are available?

- U-Net variants
- Variational Autoencoders (VAE)
- GANs
- Physics-Informed Neural Networks (PINN)

### Can I train custom models?

Yes. Prepare training data and use the training pipeline. See [ML Pipelines](ml-pipelines.md).

### Do I need a GPU?

A GPU significantly accelerates ML operations but is not required. CPU inference is supported.

---

## Deployment

### How do I install Promethium?

We recommend Docker Compose for most deployments:

```bash
docker compose -f docker/docker-compose.yml up -d
```

See [Deployment Guide](deployment-guide.md).

### Can I run Promethium without Docker?

Yes. Install Python dependencies and run services manually. See [Developer Guide](developer-guide.md).

### What are the system requirements?

Minimum: 4 CPU cores, 16 GB RAM
Recommended: 16+ cores, 64+ GB RAM, GPU

---

## Troubleshooting

### Job stuck in Pending?

Check that workers are running:

```bash
docker compose ps
```

### Poor reconstruction quality?

- Try a different model
- Check data preprocessing
- Increase ensemble runs
- Verify model matches data type

### Upload fails?

- Check file size limits
- Verify format is supported
- Check browser console for errors

---

## Support

### How do I get help?

See [SUPPORT.md](../SUPPORT.md) for support options.

### How do I report bugs?

Open a GitHub Issue with reproduction steps.

### How do I request features?

Use GitHub Discussions or open a feature request issue.

---

## Related Documents

| Document | Description |
|----------|-------------|
| [User Guide](user-guide.md) | User documentation |
| [Support](../SUPPORT.md) | Support resources |

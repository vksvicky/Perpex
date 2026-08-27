        var sysDims = dc.getTextDimensions("50%", sysFont);
        var custDims = [0, 0];
        if (customFont != null) {
            custDims = dc.getTextDimensions("50%", customFont);
        }
        System.println("DEBUG FONT - SysDims: " + sysDims[0] + "x" + sysDims[1] + " | CustDims: " + custDims[0] + "x" + custDims[1]);
